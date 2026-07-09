# 信源核验状态（2026-07-07）

## ✅ 已核验可用（3 个）

| 信源 | Feed | 说明 |
|---|---|---|
| McKinsey Insights | `https://www.mckinsey.com/insights/rss` | RSS 2.0 实测有效，组织转型/AI 战略/未来工作内容密度高，高管向天然适配 |
| a16z future | `https://future.com/rss/` | RSS 0.92 实测有效，泛科技，需按 AI/org 标签筛选 |
| Stanford HAI | newsletter 邮件订阅（非 RSS） | AI Index 年度报告含劳动力/采纳率数据；去 `hai.stanford.edu/ai-index` 留邮箱 |

## ⚠️ 待本地核验（4 个，服务器端被反爬拦截，本地阅读器大概率可用）

| 信源 | 候选 Feed | 我侧结果 | 你要做的 |
|---|---|---|---|
| HBR | `https://hbr.org/the-latest/feed` | `/the-latest/rss` 和 `/rss/` 均 404 | 浏览器开候选 URL；若 404 去 `hbr.org` 页脚找 RSS 链接 |
| MIT Sloan Review | `https://sloanreview.mit.edu/feed/` | socket hang up（疑似拦截，非 404） | 本地阅读器直接订阅试，大概率可用 |
| BCG | `https://www.bcg.com/insights/rss` | 403 | 本地阅读器试；不行去 `bcg.com/insights` 页脚 |
| Bain | `https://www.bain.com/insights/rss` | 404（路径不准） | 去 `bain.com/insights` 找正确 feed 路径 |

> 这 4 个都是核心高管向源，值得花 10 分钟本地核一遍。HBR 和 MIT Sloan 尤其重要。

## 🇨🇳 中文源（需自建 RSSHub）

公共 RSSHub 实例（rsshub.app）当前连接被拒，不可用。中文源抓取有两条路：

**方案 A：自建 RSSHub（Docker 一行起）**
```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
# 然后把 OPML 里 YOUR-RSSHUB-HOST 换成 http://localhost:1200
```
- 晚点：`/latepost/recommend`
- 36氪快讯：`/36kr/newsflashes`
- 极客公园：`/geekpark/breakingnews`

**方案 B：人工录入（推荐用于晚点这类深度源）**
- 晚点是组织向核心壁垒源，内容低频高深，人工录入反而更可控
- 公众号源（晚点/真格/红杉）可用第三方抓取工具，但有合规与稳定性风险

## 启动订阅集（最小可行 8 源）

1. McKinsey Insights ✅
2. a16z future ✅
3. Stanford HAI（邮件）
4. HBR ⚠️
5. MIT Sloan ⚠️
6. 晚点（人工或自建 RSSHub）
7. 36氪（自建 RSSHub）
8. 极客公园（自建 RSSHub）

跑通这 8 个，验证摘要+分类 pipeline 后，第二阶段再加 BCG/Bain/阿里研究院/腾讯研究院。

## 技术取舍备忘

- **质量 > 实时性**：你的站是高管情报，不是新闻聚合。McKinsey/HBR 这类有稳定 RSS 的走自动 pipeline；晚点这类深度源人工录入。
- **反爬常态化**：很多站对服务器端请求返回 403 但对 RSS 阅读器放行。你的聚合器要带正常 UA + 合理间隔，别被 ban。
- **RSSHub 自建是中文源唯一稳定路径**：公共实例常年不可用，Docker 自建 5 分钟搞定。
