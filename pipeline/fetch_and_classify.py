"""
抓取 + 分类 + 摘要 pipeline（DeepSeek 版）。

DeepSeek API 是 OpenAI 兼容的，用 openai SDK + base_url 指向 DeepSeek。
两段式：deepseek-chat 粗筛 → deepseek-chat 深加工（DeepSeek 极便宜，单模型两用）。

数据流：
  RSS 源 (直连 + RSSHub)  →  feedparser 解析
                            →  deepseek-chat 粗筛 (RELEVANCE_GATE)
                            →  deepseek-chat 深加工 (CLASSIFY_SUMMARIZE)
                            →  写入 src/data/inbox.json（站点直接消费）

依赖：
  pip install feedparser openai python-dotenv

运行：
  cd pipeline
  python fetch_and_classify.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import feedparser
from dotenv import load_dotenv
from openai import OpenAI

from aihot_source import fetch_aihot
from prompts import gate_prompt, classify_prompt

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

RSSHUB = os.environ.get("RSSHUB", "http://localhost:1200")
INBOX_PATH = Path(__file__).resolve().parent.parent / "src" / "data" / "inbox.json"
RELEVANCE_THRESHOLD = 40

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE = "https://api.deepseek.com"
GATE_MODEL = "deepseek-chat"
CLASSIFY_MODEL = "deepseek-chat"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE) if DEEPSEEK_API_KEY else None

# (name, url, tier)
FEEDS: list[tuple[str, str, str]] = [
    # —— 权威层（直连 RSS）——
    ("mckinsey", "https://www.mckinsey.com/insights/rss", "authority"),
    ("future", "https://future.com/rss/", "authority"),
    ("hbr", "https://hbr.org/the-latest/feed", "authority"),
    ("mit-sloan", "https://sloanreview.mit.edu/feed/", "authority"),
    # —— 前沿层（直连 RSS）——
    ("pragmatic-engineer", "https://newsletter.pragmaticengineer.com/feed", "frontier"),
    ("one-useful-thing", "https://www.oneusefulthing.org/feed", "frontier"),
    ("latent-space", "https://www.latent.space/feed", "frontier"),
    ("elad-gil", "https://eladgil.substack.com/feed", "frontier"),
    # —— 以下需 RSSHub，Docker 装好前先注释掉 ——
    # ("x-shreyas", f"{RSSHUB}/twitter/user/shreyas", "frontier-x"),
    # ("x-garrytan", f"{RSSHUB}/twitter/user/garrytan", "frontier-x"),
    # ("x-natfriedman", f"{RSSHUB}/twitter/user/natfriedman", "frontier-x"),
    # ("x-danielgross", f"{RSSHUB}/twitter/user/danielgross", "frontier-x"),
    # ("x-harjtaggar", f"{RSSHUB}/twitter/user/harjtaggar", "frontier-x"),
    # ("x-brendanfoody", f"{RSSHUB}/twitter/user/brendanfoody", "frontier-x"),
    # ("latepost", f"{RSSHUB}/latepost/recommend", "cn"),
    # ("36kr", f"{RSSHUB}/36kr/newsflashes", "cn"),
    # ("geekpark", f"{RSSHUB}/geekpark/breakingnews", "cn"),
]

# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------
HTML_TAG = re.compile(r"<[^>]+>")


def clean(text: str | None) -> str:
    if not text:
        return ""
    return HTML_TAG.sub("", text).strip()


def item_id(link: str, title: str) -> str:
    return hashlib.sha1(f"{link}|{title}".encode()).hexdigest()[:8]


def call_json(prompt: str, max_tokens: int = 1200, json_mode: bool = True) -> dict:
    """调 DeepSeek 并解析 JSON。DeepSeek 支持 response_format json_object。"""
    kwargs = dict(
        model=CLASSIFY_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    text = (resp.choices[0].message.content or "").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    return json.loads(text[start : end + 1])


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def fetch_feed(name: str, url: str, tier: str, timeout: int = 12) -> list[dict]:
    """用 urllib 带超时抓 feed 内容，再喂给 feedparser 解析。避免 socket hang。"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ai-org-site/0.1 (+https://github.com/zhao1bo-source/ai-org-site)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except Exception as exc:
        print(f"  [warn] {name}: 拉取失败（{exc}）")
        return []
    parsed = feedparser.parse(raw)
    if parsed.bozo and not parsed.entries:
        print(f"  [warn] {name}: 解析失败（{parsed.bozo_exception}）")
        return []
    items = []
    for e in parsed.entries:
        items.append(
            {
                "feed": name,
                "tier": tier,
                "title": clean(getattr(e, "title", "")),
                "summary": clean(getattr(e, "summary", "")),
                "link": getattr(e, "link", ""),
                "published": getattr(e, "published", ""),
            }
        )
    return items


def process_item(item: dict) -> dict | None:
    source = f"{item['feed']} ({item['tier']})"
    # aihot 条目无 published，补当天
    published = item.get("published") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # 阶段 1：粗筛
    try:
        gate = call_json(
            gate_prompt(item["title"], item["summary"][:500], source),
            max_tokens=200,
        )
    except Exception as exc:
        print(f"  [warn] gate 失败 {item['feed']}: {exc}")
        return None
    if not gate.get("relevant"):
        return None

    # 阶段 2：深加工
    try:
        result = call_json(
            classify_prompt(
                item["title"], item["summary"][:2000], source, item["link"], published
            ),
            max_tokens=1200,
        )
    except Exception as exc:
        print(f"  [warn] classify 失败 {item['feed']}: {exc}")
        return None

    if result.get("relevance_score", 0) < RELEVANCE_THRESHOLD:
        return None

    result.update(
        {
            "id": item_id(item["link"], item["title"]),
            "feed": item["feed"],
            "tier": item["tier"],
            "title": item["title"],
            "link": item["link"],
            "published": published,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return result


def main() -> None:
    if not client:
        print("❌ 未配置 DEEPSEEK_API_KEY，请检查 .env")
        return
    print(f"== pipeline 启动 @ {datetime.now(timezone.utc).isoformat()} ==")
    all_items: list[dict] = []

    # —— RSS 直连源 ——
    for name, url, tier in FEEDS:
        print(f"[fetch] {name} ({tier})")
        items = fetch_feed(name, url, tier)
        print(f"  拉到 {len(items)} 条")
        kept = 0
        for item in items:
            result = process_item(item)
            if result:
                all_items.append(result)
                kept += 1
            time.sleep(0.3)
        print(f"  入库 {kept} 条")

    # —— aihot 大池子（含 X 等多源，已人工粗筛）——
    print(f"[fetch] aihot (frontier, 大池子)")
    try:
        aihot_items = fetch_aihot()
        print(f"  拉到 {len(aihot_items)} 条")
        kept = 0
        for item in aihot_items:
            result = process_item(item)
            if result:
                all_items.append(result)
                kept += 1
            time.sleep(0.3)
        print(f"  入库 {kept} 条（aihot 多为模型发布，组织变革相关的命中率较低属正常）")
    except Exception as exc:
        print(f"  [warn] aihot 抓取失败: {exc}")

    # 去重
    seen, deduped = set(), []
    for r in all_items:
        if r["id"] not in seen:
            seen.add(r["id"])
            deduped.append(r)

    INBOX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(INBOX_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"generated_at": datetime.now(timezone.utc).isoformat(), "items": deduped},
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"== 完成：入库 {len(deduped)} 条 → {INBOX_PATH} ==")


if __name__ == "__main__":
    main()
