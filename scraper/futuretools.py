"""FutureTools.io AI News 抓取

FutureTools 是 Matt Wolfe 运营的 AI 资讯聚合站，每日更新，
内容覆盖 AI 工具、融资、产品发布，结构非常规整。

页面地址: https://futuretools.io/news
"""
from playwright.sync_api import sync_playwright
from scraper.base import RawItem, save_items
from config.settings import RAW_DIR, MAX_RAW_ITEMS


def scrape() -> list[RawItem]:
    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://futuretools.io/news", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            # FutureTools 的新闻卡片结构：
            # 每条新闻是一个 <a> 链接块，包含标题和摘要
            # 选择器可能需要根据实际 DOM 微调
            cards = page.query_selector_all("a[href*='utm_source=futuretools']")

            for card in cards[:MAX_RAW_ITEMS]:
                # 标题通常是卡片内的第一个文本块
                title_el = card.query_selector("h2, h3, [class*='title'], [class*='heading']")
                # 摘要/TLDR
                summary_el = card.query_selector("p, [class*='summary'], [class*='description'], [class*='tldr']")

                title = title_el.inner_text().strip() if title_el else card.inner_text()[:100].strip()
                summary = summary_el.inner_text().strip()[:500] if summary_el else ""
                url = card.get_attribute("href") or ""

                # 提取来源信息（通常在卡片内显示）
                source_el = card.query_selector("[class*='source'], [class*='domain'], span")
                source_name = source_el.inner_text().strip() if source_el else "futuretools"

                item = RawItem(
                    source="futuretools",
                    title=title,
                    summary=summary,
                    source_url=url,
                    author=source_name,
                )
                if item.is_valid() and len(item.title) > 10:
                    items.append(item)

        except Exception as e:
            print(f"  [futuretools] Error: {e}")
        finally:
            browser.close()

    return items


def run():
    print("  [futuretools] Scraping https://futuretools.io/news ...")
    items = scrape()
    if items:
        save_items(items, "futuretools", RAW_DIR)
    else:
        print("  [futuretools] No items scraped — check selectors")
    return items


if __name__ == "__main__":
    run()
