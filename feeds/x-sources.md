# X 源清单 + RSSHub 路由

> 原则：有 RSS 主阵地的人走 RSS（见 frontier-sources.md），X 只抓真正 X-only 的人。
> X 是高噪音源，必须经 pipeline 的相关度过滤（见 pipeline/prompts.py）。

## 最终 X-only 账号（6 个）

| 账号 | handle | RSSHub 路由 | 为什么留 X |
|---|---|---|---|
| Shreyas Doshi | @shreyas | `/twitter/user/shreyas` | 主要阵地就是 X，产品/组织思考 |
| Garry Tan | @garrytan | `/twitter/user/garrytan` | YC，创业组织，X 为主 |
| Nat Friedman | @natfriedman | `/twitter/user/natfriedman` | AI 投资+组织观察，X 为主 |
| Daniel Gross | @danielgross | `/twitter/user/danielgross` | 同上，常与 Nat 联动 |
| Harj Taggar | @harjtaggar | `/twitter/user/harjtaggar` | hiring/org，A-Player |
| Brendan Foody | @brendanfoody | `/twitter/user/brendanfoody` | Mercor CEO，AI-native 雇佣（公司 blog 在 HTML 抓取层补充） |

> Walden Yan (@waldenyan) 暂不进 X 层——Cognition blog 已在 HTML 抓取层覆盖，避免重复。若 blog 更新太慢再补 X。

## 完整 RSSHub 路由表（X 层，本地实例 :1200）

```
http://localhost:1200/twitter/user/shreyas
http://localhost:1200/twitter/user/garrytan
http://localhost:1200/twitter/user/natfriedman
http://localhost:1200/twitter/user/danielgross
http://localhost:1200/twitter/user/harjtaggar
http://localhost:1200/twitter/user/brendanfoody
```

## cookie 获取（一次性，每 2-4 周更新）

1. 浏览器登录 x.com
2. DevTools → Application → Cookies → `https://x.com`
3. 复制两个值：
   - `auth_token` → 填入 `TWITTER_AUTH_TOKEN`
   - `ct0` → 填入 `TWITTER_CT0`
4. 写入项目根目录 `.env`（见 .env.example）

> cookie 失效时 RSSHub 会返回错误，pipeline 的 fetch 层会跳过该源并记日志。
> 用一个小号提供 cookie，降低主号风险。

## 反噪音策略

X 这 6 个账号日均产出 50+ 条，其中 AI 组织相关可能不到 10%。pipeline 的做法：
1. 先用便宜模型（Haiku）做粗筛：title+summary 判断是否 org 相关 → 不相关直接丢
2. 相关的再用强模型（Sonnet/Opus）做四支柱分类 + 高管启示
3. 这样既控成本又保质量（见 prompts.py 的两段式设计）
