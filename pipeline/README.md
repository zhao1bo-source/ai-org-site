# Pipeline：抓取 + 分类 + 摘要

把 17 个信源（权威层 + 前沿层 + X + 中文）统一拉取、去重、按四支柱分类、生成高管启示，输出到 `content/inbox.json` 供站点渲染。

## 一次架构图

```
  RSS 直连源                RSSHub (Docker :1200)
  ─────────                 ──────────────────────
  McKinsey                  X 账号 (/twitter/user/*)    ← 需 TWITTER cookie
  Pragmatic Engineer        中文源 (晚点/36氪/极客公园)
  Mollick / Latent Space
  Elad Gil
        │                           │
        └──────────┬────────────────┘
                   ▼
           feedparser 解析
                   ▼
         Haiku 粗筛 (RELEVANCE_GATE)   ← 丢掉非组织相关
                   ▼
       Sonnet 深加工 (CLASSIFY_SUMMARIZE)
         四支柱分类 + 相关度打分 + 高管启示
                   ▼
           content/inbox.json  ──→  站点渲染
```

## 依赖

```bash
pip install feedparser anthropic
```

## 首次运行

```bash
# 1. 起 RSSHub（项目根目录）
cp .env.example .env          # 填 TWITTER_AUTH_TOKEN / TWITTER_CT0
docker compose up -d
curl http://localhost:1200/twitter/user/shreyas   # 验证 X 路由能拉到内容

# 2. 配 API key
export ANTHROPIC_API_KEY=sk-...

# 3. 跑 pipeline
cd pipeline
python fetch_and_classify.py
```

输出：`content/inbox.json`，每条结构：

```json
{
  "id": "a3f9c2b1...",
  "feed": "pragmatic-engineer",
  "tier": "frontier",
  "pillar": "case",
  "relevance_score": 82,
  "tags": ["科技", "大厂", "agent"],
  "structured_summary": {
    "background": "...",
    "decision_action": "...",
    "result": "...",
    "lesson": "..."
  },
  "executive_takeaway": "一句话高管启示",
  "signal_strength": "high",
  "title": "...",
  "link": "...",
  "published": "...",
  "ingested_at": "..."
}
```

## 关键设计决策

### 1. 两段式 LLM 调用（省钱）
- X 是高噪音源（6 个号日均 50+ 条，相关不到 10%）
- 先 Haiku 粗筛（便宜），再 Sonnet 深加工（贵但只跑相关的）
- 单次全量跑约：50 次 Haiku + 5 次 Sonnet，成本可控

### 2. 相关度门控 (RELEVANCE_THRESHOLD=40)
- 低于 40 分直接丢，不进 inbox
- 调高→更精准但少内容；调低→更全但噪音多
- 建议先跑一遍看分布，再定阈值

### 3. signal_strength（热点榜排序用）
- high：裁员/重组/CEO 备忘录 → 替代 aihot 的"多源热度"逻辑
- medium：流程/工具变化
- low：趋势/观点/数据
- 这是高管视角的"信号强度"，不是媒体热度

### 4. executive_takeaway 是核心差异化
- aihot 给"推荐理由"，我们给"高管可行动判断"
- 30 字以内，必须带判断（不是复述）
- 这是站点相对 aihot 的最大壁垒

## 增量运行 / 调度

当前是全量跑。增量建议：
- inbox.json 已有 id 去重，重复条目不会重复入库
- 用 cron / launchd 每日跑 1-2 次（X 日级即可，不需要实时）
- ```bash
  # crontab 示例：每天 8 点、20 点
  0 8,20 * * * cd /Users/zhao1bo/ai-org-site && python pipeline/fetch_and_classify.py >> logs/pipeline.log 2>&1
  ```

## 待办 / 已知限制

- [ ] HBR / MIT Sloan 的 RSS 端点待本地核验（见 feeds/STATUS.md）
- [ ] HTML 抓取层（Cognition / Mercor blog）未接入——需写轻量 scraper，比 RSS 多一层
- [ ] cookie 失效检测：当前 RSSHub 报错只打 warn 跳过，可加告警
- [ ] 增量模式：当前全量重跑，量大后改为只拉最近 N 小时
