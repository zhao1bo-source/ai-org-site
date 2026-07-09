# AI 组织变革情报站

面向高管的 AI 组织变革情报站。聚合权威源（McKinsey/HBR/HAI）与前沿实践（Pragmatic Engineer/Mollick/X 创始人），按四支柱分类，提炼可行动的高管启示。

对标 aihot.virxact.com，但定位不同：aihot 面向开发者做动态聚合，本站面向高管做**决策情报**。

## 线上

**https://zhao1bo-source.github.io/ai-org-site/**（GitHub Pages，push 到 main 自动部署）

## 内容四支柱

| 支柱 | 含义 |
|---|---|
| case 案例 | 公司真实的组织/人力/流程决策 + 可观测结果 |
| theory 理论 | 可复用的模型、原则、分类法 |
| memo 备忘录 | CEO/CIO 内部信、财报表态、创始人观点 |
| data 数据 | 调研、统计、量化指标 |

## 架构

```
信源（RSS 直连 + RSSHub）  →  pipeline（DeepSeek 两段式）  →  inbox.json  →  Astro 站点
   17 个源                    粗筛(Haiku级) + 深加工             schema 载体        静态生成
```

### 信源分层
- **权威层**：McKinsey / HBR / MIT Sloan / Stanford HAI / a16z future（直连 RSS）
- **前沿层**：Pragmatic Engineer / Mollick / Latent Space / Elad Gil（直连 RSS）
- **X 层**：Shreyas / Garry Tan / Nat Friedman 等 6 人（经 RSSHub，需 cookie）
- **中文源**：晚点 / 36氪 / 极客公园（经 RSSHub）

信源详情见 `feeds/`。RSSHub 配置见 `docker-compose.yml`。

### pipeline（`pipeline/`）
- `fetch_and_classify.py`：抓取 → DeepSeek 粗筛（丢噪音）→ DeepSeek 深加工（四支柱分类 + 高管启示）→ 写 `src/data/inbox.json`
- `prompts.py`：两段式 prompt。**强制中文输出**，无论源语言
- 两段式省钱：粗筛用便宜调用丢掉 90% 不相关，深加工只跑相关的

### 站点（`src/`）
- Astro 静态生成，读 `src/data/inbox.json`
- 首页：时间线 + 四支柱×层级双筛选 + 信号强度榜
- 详情页：背景/决策动作/可观测结果/启示 结构化深页
- 四支柱列表页 + 周报页

## 本地开发

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # 产出 dist/
```

## 跑 pipeline 生成内容

```bash
# 1. 配 DeepSeek key
cp .env.example .env   # 填 DEEPSEEK_API_KEY

# 2. 跑
cd pipeline
../.venv/bin/python fetch_and_classify.py

# 3. inbox.json 更新后，提交推送即自动部署
git add src/data/inbox.json && git commit -m "更新内容" && git push
```

## RSSHub（X + 中文源）

```bash
# Docker（OrbStack/Docker Desktop）已运行时
docker compose up -d
# 验证
curl http://localhost:1200/36kr/newsflashes
```

X 路由需在 `.env` 填 `TWITTER_AUTH_TOKEN` 和 `TWITTER_CT0`（浏览器 x.com → DevTools → Cookies）。
晚点 latepost 路由在当前 RSSHub 版本有 bug，按人工录入处理。

## 部署

GitHub Actions（`.github/workflows/deploy.yml`）：push 到 main → Astro 构建 → 部署到 GitHub Pages。
Pages 源已设为 GitHub Actions（build_type=workflow）。

## 待办

- [ ] HBR / MIT Sloan RSS 端点本地核验（服务器侧 403/404）
- [ ] 接入 X cookie 后启用 X 层 6 个源
- [ ] Cognition / Mercor blog HTML 抓取层
- [ ] pipeline 增量运行 + 定时调度（cron）
