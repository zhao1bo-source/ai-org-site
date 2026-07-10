"""
aihot.virxact.com 抓取器（官方公开 API 版）。

aihot 提供无需认证的公开 REST API（测试版）：
  GET /api/public/items?mode=selected  精选条目
  GET /api/public/items?mode=all       全部条目

返回结构化 JSON（title/summary/source/publishedAt/category/score/permalink/url），
比 HTML 抓取稳定得多。aihot 已对 X 等多源做人工筛选，这里把它作为"大池子"，
再交给 pipeline 两段式粗筛，只留 AI 组织变革相关的。

API 文档：https://aihot.virxact.com/agent
"""

from __future__ import annotations

import json
import urllib.request

AIHOT_API = "https://aihot.virxact.com/api/public/items"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ai-org-site/0.1"


def fetch_aihot(mode: str = "all", timeout: int = 20) -> list[dict]:
    """调 aihot 公开 API，返回归一化后的条目列表。

    mode: "all"（全部，默认，最大化池子）或 "selected"（仅精选）。
    """
    url = f"{AIHOT_API}?mode={mode}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    raw_items = data.get("items", []) if isinstance(data, dict) else data
    items: list[dict] = []
    for r in raw_items:
        title = (r.get("title") or "").strip()
        if not title:
            continue
        summary = (r.get("summary") or "").strip()
        source = r.get("source") or ""
        if source:
            summary = f"[{source}] {summary}"
        items.append(
            {
                "feed": "aihot",
                "tier": "frontier",
                "title": title,
                "summary": summary,
                # link 用原文 url（全文抓取需要），permalink 备用
                "link": r.get("url") or r.get("permalink") or "",
                "published": (r.get("publishedAt") or "")[:10],  # YYYY-MM-DD
                "tags_hint": [r.get("category", "")] if r.get("category") else [],
                "source_hint": source,
            }
        )
    return items


if __name__ == "__main__":
    items = fetch_aihot()
    print(f"抓到 {len(items)} 条\n")
    for it in items[:6]:
        print(f"[{it['source_hint']}] {it['title'][:55]}")
        print(f"  摘要: {it['summary'][:90]}")
        print(f"  分类: {it['tags_hint']} | 日期: {it['published']}")
        print()
