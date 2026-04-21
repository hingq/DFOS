"""The Rundown AI 抓取

全球最大的 AI newsletter（200万+订阅者），每日更新。
抓取其公开的 archive 页面获取最新文章标题和链接。

页面地址: https://www.therundown.ai/archive/
"""
from playwright.sync_api import sync_playwright
from scraper.base import RawItem, save_items
from config.settings import RAW_DIR


def scrape() -> list[RawItem]:
    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://www.therundown.ai/archive/", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            # The Rundown 的 archive 页面是 Beehiiv 平台
            # 文章列表通常是 <a> 标签包含文章标题
            links = page.query_selector_all("a[href*='/p/']")

            seen_urls = set()
            for link in links[:20]:
                url = link.get_attribute("href") or ""
                if not url or url in seen_urls or "/p/" not in url:
                    continue
                seen_urls.add(url)

                title = link.inner_text().strip()
                if not title or len(title) < 10:
                    continue

                # 确保 URL 是完整的
                if url.startswith("/"):
                    url = f"https://www.therundown.ai{url}"

                item = RawItem(
                    source="therundown",
                    title=title,
                    summary="",  # archive 页面通常只有标题
                    source_url=url,
                    author="Rowan Cheung",
                )
                items.append(item)

        except Exception as e:
            print(f"  [therundown] Error: {e}")
        finally:
            browser.close()

    return items


def run():
    print("  [therundown] Scraping https://www.therundown.ai/archive/ ...")
    items = scrape()
    if items:
        save_items(items, "therundown", RAW_DIR)
    else:
        print("  [therundown] No items scraped — check selectors")
    return items


if __name__ == "__main__":
    run()
