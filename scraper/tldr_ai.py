"""TLDR AI 抓取

技术侧 AI 资讯 newsletter，50万+订阅者，工作日每天更新。
简洁无废话，每条只有一段摘要+链接。

页面地址: https://tldr.tech/ai/archives
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
            # TLDR 有公开的 archive 页面
            page.goto("https://tldr.tech/ai/archives", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            # 点击最新一期进入详情页
            latest_link = page.query_selector("a[href*='/ai/']")
            if latest_link:
                latest_url = latest_link.get_attribute("href")
                if latest_url:
                    if latest_url.startswith("/"):
                        latest_url = f"https://tldr.tech{latest_url}"
                    page.goto(latest_url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(2000)

            # TLDR 的每期 newsletter 内容结构：
            # 标题通常是 <h3> 或加粗链接，后跟一段摘要文本
            articles = page.query_selector_all("article a, h3 a, [class*='article'] a")

            seen = set()
            for article in articles[:30]:
                title = article.inner_text().strip()
                url = article.get_attribute("href") or ""

                if not title or len(title) < 10 or title in seen:
                    continue
                if "tldr.tech" in url and "/ai/" in url:
                    continue  # 跳过内部导航链接
                seen.add(title)

                item = RawItem(
                    source="tldr_ai",
                    title=title,
                    summary="",
                    source_url=url,
                    author="TLDR AI",
                )
                items.append(item)

        except Exception as e:
            print(f"  [tldr_ai] Error: {e}")
        finally:
            browser.close()

    return items


def run():
    print("  [tldr_ai] Scraping https://tldr.tech/ai/archives ...")
    items = scrape()
    if items:
        save_items(items, "tldr_ai", RAW_DIR)
    else:
        print("  [tldr_ai] No items scraped — check selectors")
    return items


if __name__ == "__main__":
    run()
