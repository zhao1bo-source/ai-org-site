# 前沿信源层（Frontier Sources）

> 区别于 McKinsey/HBR 的"后视镜"源，前沿层抓 AI-native 创业公司的一手组织实践。
> 已核验 RSS 的可直接进 pipeline；无 RSS 的走 HTML 抓取或人工录入。

## ✅ 已核验 RSS 可用（强烈推荐，这层比咨询报告领先 3-6 个月）

| 信源 | Feed | 价值 | 实证 |
|---|---|---|---|
| **The Pragmatic Engineer** (Gergely Orosz) | `https://newsletter.pragmaticengineer.com/feed` | 工程 org + AI 实践，前线报道 | 实测："Impressions from visiting OpenAI/Anthropic/Cursor"——OpenAI 95% 非工程师用 Codex；"Why is Meta destroying its engineering org?" |
| **One Useful Thing** (Ethan Mollick, Wharton) | `https://www.oneusefulthing.org/feed` | AI 在工作中的采纳，引用一手研究 | 实测："twilight of chatbots" 引用 OpenAI/经济学家联合研究；agentic AI 跨职能采纳 |
| **Latent Space** (Swyx) | `https://www.latent.space/feed` | Agent 工程 + 工程 org | 实测：Vercel 谈 "agents are a new kind of software"、skill engineering |

> 这三个是金矿。Pragmatic Engineer 尤其——它做的正是你要做的事（去前沿公司探访+报道组织实践），可以直接作为你内容的方法论参照。

## ⚠️ 无 RSS，需 HTML 抓取（内容极值钱）

| 公司/Blog | URL | 价值 |
|---|---|---|
| **Cognition (Devin)** | `https://cognition.com/blog` | "How Cognition Uses Devin to Build Devin"、"Devin's 2025 Performance Review"、"AI Productivity Guarantee"——AI-native 公司如何用自己产品组织工程 |
| **Mercor** | `https://www.mercor.com/blog` | AI-native 招聘/雇佣，组织模式前沿 |
| **Factory** | `https://factory.ai/blog` | Agent 公司组织实践 |
| **Cursor / Anysphere** | 官方 blog | 编辑器+团队组织 |

> 建议写一个轻量 HTML scraper（按域名 selectors 定时抓 blog 列表页），比 X 抓取稳定 10 倍。

## 🐦 X 层（一手创始人观点，最难聚合但最前沿）

X 无开放 RSS，反爬严。三条路径，按推荐度排序：

### 路径 1：X Lists + 人工/半自动巡检（推荐起步）
建一个 X List，把这些人放进去，每天人工扫一遍 + agent 辅助摘要。
**必关注账号（按 AI 组织变革相关度）：**

| 人 | 为什么关注 |
|---|---|
| **Gergely Orosz** (@GergelyOrosz) | Pragmatic Engineer 作者，前线组织报道，X 上比 newsletter 更快 |
| **Ethan Mollick** (@emollick) | Wharton，AI 工作实践，引用研究第一时间 |
| **Shreyas Doshi** (@shreyas) | 产品/组织，硅谷最有影响力的 org 思考者之一 |
| **Brendan Foody** (@brendanfoody) | Mercor CEO，AI-native 雇佣 |
| **Walden Yan** (@waldenyan) | Cognition，工程 org 实践 |
| **Patrick Collison** (@patrickc) | Stripe CEO，写组织/计算 |
| **Elad Gil** (@eladgil) | 高增长/组织，深度博客 |
| **Garry Tan** (@garrytan) | YC，创业组织 |
| **Nat Friedman** (@natfriedman) / **Daniel Gross** (@danielgross) | AI 投资+组织观察 |
| **Dwarkesh Patel** (@dwarkesh_) | 播客，深度访谈 AI 公司创始人讲组织 |
| **Harj Taggar** (@harjtaggar) | A-Player，hiring/org |

> 高管备忘录类：追踪大厂 CEO 公开信（Tobi Lutke @tobi, Zuckerberg, 等），这类一手材料价值极高。

### 路径 2：自建 RSSHub + X 路由（需 cookie）
RSSHub 支持 X 用户路由（`/twitter/user/:id`），但 X 强制登录 + 频繁封 cookie。
- 需要一个 X 账号提供 cookie token
- cookie 寿命短，维护成本高
- 适合少量核心账号（5-10 个），不适合大规模

### 路径 3：第三方 X→RSS 服务（如 rss-bridge / nitter 已基本失效）
Nitter 实例 2024 后基本全死，不推荐依赖。

## 推荐的"前沿层"启动集（最小可行）

```
RSS 自动（已验）：
1. Pragmatic Engineer   ✅
2. One Useful Thing     ✅
3. Latent Space         ✅

HTML 抓取（需写 scraper）：
4. Cognition blog
5. Mercor blog

X 人工/半自动（List 巡检）：
6. 上面 11 个账号的 List
```

跑通这 6 个，前沿层就立住了。与第一层的权威源叠加：**权威源给趋势判断，前沿源给当下实践**——这正是高管需要的两层结构。
