"""Fetch three recent multimodal-AI items from public RSS feeds.

This intentionally records source links and short feed excerpts. It does not
pretend that an automated feed is a human-written analysis; deeper commentary
can be added later in a separate learning note.
"""

from __future__ import annotations

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path


FEEDS = [
    "https://huggingface.co/blog/feed.xml",
    "https://blog.google/technology/ai/rss/",
]
KEYWORDS = (
    "multimodal",
    "vision",
    "visual",
    "video",
    "image",
    "audio",
    "speech",
    "gemini",
    "vlm",
    "agentic",
)


def clean(value: str) -> str:
    value = html.unescape(value or "")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "multimodal-agent-evaluation-handbook/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def items(feed: bytes, source: str) -> list[dict[str, str]]:
    root = ET.fromstring(feed)
    results = []
    for item in root.findall(".//item"):
        title = clean(item.findtext("title"))
        link = clean(item.findtext("link"))
        date = clean(item.findtext("pubDate") or item.findtext("published"))
        description = clean(item.findtext("description"))
        searchable = f"{title} {description}".lower()
        if title and link and any(keyword in searchable for keyword in KEYWORDS):
            results.append({"title": title, "link": link, "date": date, "description": description, "source": source})
    return results


def main() -> None:
    collected = []
    for feed_url in FEEDS:
        try:
            collected.extend(items(fetch(feed_url), feed_url))
        except Exception as exc:  # keep one broken feed from stopping the daily job
            print(f"Warning: could not fetch {feed_url}: {exc}")

    seen = set()
    selected = []
    for item in collected:
        if item["link"] in seen:
            continue
        seen.add(item["link"])
        selected.append(item)
        if len(selected) == 3:
            break

    shanghai_now = datetime.now(timezone.utc) + timedelta(hours=8)
    today = shanghai_now.date().isoformat()
    output = Path("docs/daily-learning") / f"{today}-multimodal-news.md"
    if output.exists():
        print(f"Keeping existing curated note: {output}")
        return
    lines = [
        f"# {today}｜多模态模型每日情报",
        "",
        "> 自动抓取自公开 RSS。先记录事实与来源，再由人工补充判断；不把自动摘要当作完整测评结论。",
        "",
    ]
    if not selected:
        lines.append("今天未能从配置的信息源抓到符合筛选条件的条目，请手动补充。")
    else:
        for index, item in enumerate(selected, start=1):
            excerpt = item["description"][:500].rstrip(" .")
            lines.extend(
                [
                    f"## {index}. {item['title']}",
                    "",
                    f"- 来源：[{item['source']}]({item['source']})",
                    f"- 原文：[{item['link']}]({item['link']})",
                    f"- 发布时间：{item['date'] or '未提供'}",
                    f"- 摘要：{excerpt or '请打开原文查看详情。'}",
                    "- 与我的学习关系：待补充——重点关注输入模态、实时性、评测指标、成本和失败边界。",
                    "",
                ]
            )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output} with {len(selected)} item(s)")


if __name__ == "__main__":
    main()
