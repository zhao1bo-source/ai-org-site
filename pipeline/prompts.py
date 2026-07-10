"""
分类 + 摘要 prompt 层。

两段式设计（控成本 + 保质量）：
  1. RELEVANCE_GATE  —— Haiku 粗筛：是否 AI 组织变革相关？输出 {relevant: bool, reason}
  2. CLASSIFY_SUMMARIZE —— Sonnet/Opus 深加工：四支柱分类 + 相关度打分 + 高管启示

四支柱（与站点内容分类法一致）：
  case     实践案例：公司真实的组织/人力/流程决策与可观测结果
  theory   理论与框架：可被复用的模型、原则、分类法
  memo     高管备忘录/观点：CEO/CIO 内部信、财报表态、创始人一手观点
  data     调研与数据：统计、调研、量化指标
"""

# ---------------------------------------------------------------------------
# 阶段 1：相关度门控（便宜模型，高召回）
# ---------------------------------------------------------------------------
RELEVANCE_GATE = """你是一个内容筛子。判断下面这条内容是否与"AI 驱动的组织变革"相关。

相关的标准（满足任一即可）：
- 描述某公司/团队因 AI 做了组织、人力、流程、汇报关系、招聘、考核上的真实决策
- 给出可复用的组织设计框架、原则、分类法（如 agent 自治光谱、principal-agent）
- 高管/创始人对 AI 组织变革的一手观点或内部备忘录
- AI 采纳率、对就业/岗位/技能的调研数据或量化结果

不相关（直接判 false）：
- 纯模型能力发布、跑分、API 更新（除非连带组织影响）
- 纯产品功能、融资、估值（除非连带组织决策）
- 通用技术教程、个人感悟、行业八卦

内容：
标题：{title}
摘要：{summary}
来源：{source}

只输出 JSON：
{{"relevant": true/false, "reason": "一句话"}}"""


# ---------------------------------------------------------------------------
# 阶段 2：分类 + 结构化摘要 + 高管启示（强模型）
# ---------------------------------------------------------------------------
CLASSIFY_SUMMARIZE = """你是面向企业高管的 AI 组织变革情报分析师。把下面这条内容加工成结构化情报。

**语言要求：无论原文是中文还是英文，所有输出字段（structured_summary、executive_takeaway、tags）一律用简体中文。** 英文源内容在理解后直接用中文产出，不要保留英文，不要做"翻译腔"。

内容：
标题：{title}
摘要：{summary}
来源：{source}
链接：{link}
时间：{published}

任务：按四支柱分类，并产出结构化摘要。四支柱定义：
- case     实践案例：某公司真实的组织/人力/流程决策 + 可观测结果
- theory   理论与框架：可复用的模型、原则、分类法
- memo     高管备忘录/观点：一手内部信、财报表态、创始人观点
- data     调研与数据：统计、调研、量化指标

高管启示是核心——不要复述内容，要回答："一个正在考虑用 AI 重塑组织的高管，能从这条内容里拿走什么可行动的判断？"

只输出 JSON：
{{
  "pillar": "case|theory|memo|data",
  "relevance_score": 0-100,
  "tags": ["行业", "公司规模", "关键概念"],
  "structured_summary": {{
    "background": "背景：这件事发生在什么场景",
    "decision_action": "决策与动作：具体做了什么",
    "result": "可观测结果：有数据写数据，没有写'待验证'",
    "lesson": "启示：对高管的可行动判断"
  }},
  "executive_takeaway": "一句话高管启示，30字以内，要带判断",
  "signal_strength": "low|medium|high"
}}

signal_strength 含义（用于热点榜排序）：
- high   组织变革信号强：裁员/重组/CEO 备忘录/明确替代人力的决策
- medium 间接信号：流程变化、工具采纳、招聘转向
- low    背景信息：趋势、观点、数据"""


def gate_prompt(title: str, summary: str, source: str) -> str:
    return RELEVANCE_GATE.format(title=title, summary=summary, source=source)


def classify_prompt(
    title: str, summary: str, source: str, link: str, published: str
) -> str:
    return CLASSIFY_SUMMARIZE.format(
        title=title,
        summary=summary,
        source=source,
        link=link,
        published=published,
    )


# ---------------------------------------------------------------------------
# 阶段 3：翻译原文 + 关键内容标注（一次调用产出中文译文 + 标注）
# ---------------------------------------------------------------------------
ANNOTATE = """你是面向企业高管的 AI 组织变革情报分析师。下面是一篇文章的原文全文。请完成两件事：

1. **把全文翻译成简体中文**（content 字段）。要求：完整翻译，保留段落结构，专业术语准确，不要省略，不要加译注。如果原文已是中文，直接保留原文。
2. **在中文译文上标注关键内容**（annotations 字段）。quote 必须是从你翻译的中文译文里截取的原话（逐字一致，用于在译文里高亮定位）。

标注三类关键内容（每类挑最重要的 2-4 条，宁缺毋滥）：
- data      关键数据/指标：具体数字、比例、规模、金额、增长率等
- decision  关键决策/动作：公司/团队具体做了什么决策或动作
- insight   关键观点/启示：值得高管记住的判断性语句

quote 截取原则：长度 15-80 字，是中文译文里的连续原话，能独立理解，必须与译文文本完全一致。

原文全文：
{fulltext}

只输出 JSON：
{{
  "content": "翻译后的中文全文",
  "annotations": [
    {{"type": "data", "quote": "中文译文里的原话", "note": "中文说明这条数据为何重要"}},
    {{"type": "decision", "quote": "中文译文里的原话", "note": "中文说明这个决策的含义"}},
    {{"type": "insight", "quote": "中文译文里的原话", "note": "中文说明这个观点的启示"}}
  ]
}}"""


def annotate_prompt(fulltext: str) -> str:
    return ANNOTATE.format(fulltext=fulltext)
