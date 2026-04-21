"""Autocli 页面抓取

使用 Playwright 抓取 Autocli 聚合页面内容。
请根据实际页面结构调整 selectors。
"""
from playwright.sync_api import sync_playwright
from scraper.base import RawItem, save_items
from config.settings import AUTOCLI_URL, RAW_DIR, MAX_RAW_ITEMS


def scrape_autocli() -> list[RawItem]:
    """抓取 Autocli 聚合页面"""
    if not AUTOCLI_URL:
        print("  [autocli] AUTOCLI_URL not configured, skipping")
        return []

    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(AUTOCLI_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)  # 等待动态内容加载

            # ============================================================
            # TODO: 根据 Autocli 实际页面结构调整以下选择器
            # ============================================================
            cards = page.query_selector_all(".item-card")

            for card in cards[:MAX_RAW_ITEMS]:
                title_el = card.query_selector(".title")
                summary_el = card.query_selector(".summary")
                link_el = card.query_selector("a")

                item = RawItem(
                    source="autocli",
                    title=title_el.inner_text().strip() if title_el else "",
                    summary=summary_el.inner_text().strip() if summary_el else "",
                    source_url=link_el.get_attribute("href") or "" if link_el else "",
                )
                if item.is_valid():
                    items.append(item)

        except Exception as e:
            print(f"  [autocli] Error: {e}")
        finally:
            browser.close()

    return items


def run():
    """执行抓取并保存"""
    print("  [autocli] Scraping...")
    items = scrape_autocli()
    if items:
        save_items(items, "autocli", RAW_DIR)
    else:
        print("  [autocli] No items scraped")
    return items


if __name__ == "__main__":
    run()
