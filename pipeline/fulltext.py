"""
原文全文抓取 + 正文提取。

用 trafilatura 从网页提取正文（去导航/评论/广告噪音）。
部分源反爬抓不到（McKinsey 超时、HBR/MIT Sloan 403），返回 None 走 fallback。
"""

from __future__ import annotations

import re
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
MIN_LEN = 200  # 正文过短视为无效


def fetch_fulltext(url: str, timeout: int = 12) -> str | None:
    """抓网页，提取正文。失败返回 None。"""
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", "ignore")
    except Exception:
        return None

    # 优先用 trafilatura 提取
    try:
        import trafilatura

        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
        if text and len(text) >= MIN_LEN:
            return text.strip()
    except Exception:
        pass

    # fallback：简单 <p> 聚合
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html, re.S)
    text = "\n\n".join(re.sub(r"<[^>]+>", "", p).strip() for p in paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) >= MIN_LEN:
        return text
    return None


if __name__ == "__main__":
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "https://newsletter.pragmaticengineer.com/p/why-is-meta-destroying-its-engineering"
    t = fetch_fulltext(url)
    if t:
        print(f"✅ 提取 {len(t)} 字符\n")
        print(t[:500])
    else:
        print("❌ 抓取失败")
