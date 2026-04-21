"""RSS 通用抓取

使用 feedparser 解析所有已启用的 RSS 信源。
"""
import ssl
import certifi
import urllib.request
import feedparser
from scraper.base import RawItem, save_items
from config.sources import get_rss_sources
from config.settings import RAW_DIR

# 创建使用 certifi 证书的 SSL 上下文
_ssl_context = ssl.create_default_context(cafile=certifi.where())

# 添加 User-Agent 请求头
_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml,application/xml,text/xml,*/*",
}


def scrape_rss_feed(source: dict) -> list[RawItem]:
    """抓取单个 RSS 源"""
    items = []
    try:
        # 使用 urllib 获取内容，然后用 certifi 证书
        req = urllib.request.Request(source["url"], headers=_headers)
        with urllib.request.urlopen(req, context=_ssl_context) as response:
            content = response.read()
        feed = feedparser.parse(content)
        for entry in feed.entries[:20]:
            item = RawItem(
                source=source["name"],
                title=getattr(entry, "title", ""),
                summary=getattr(entry, "summary", "")[:500],
                source_url=getattr(entry, "link", ""),
                author=getattr(entry, "author", ""),
                published_at=getattr(entry, "published", ""),
                tags=[t.get("term", "") for t in getattr(entry, "tags", [])],
            )
            if item.is_valid():
                items.append(item)
    except Exception as e:
        print(f"  [rss:{source['name']}] Error: {e}")

    return items


def run():
    """抓取所有已启用的 RSS 源"""
    rss_sources = get_rss_sources()
    if not rss_sources:
        print("  [rss] No enabled RSS sources")
        return []

    all_items = []
    for source in rss_sources:
        print(f"  [rss:{source['name']}] Fetching...")
        items = scrape_rss_feed(source)
        all_items.extend(items)

    if all_items:
        save_items(all_items, "rss", RAW_DIR)

    print(f"  [rss] Total: {len(all_items)} items from {len(rss_sources)} sources")
    return all_items


if __name__ == "__main__":
    run()
