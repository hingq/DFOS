"""Product Hunt 首页抓取

抓取 https://www.producthunt.com/ 当天的热门产品。
Product Hunt 使用 data-test 属性，比 class 名更稳定。

注意：Product Hunt 有反爬措施，需要设置合理的 user-agent 和等待时间。
如果抓取不稳定，备选方案是用 RSS feed（已在 config/sources.py 中配置）。
"""
from playwright.sync_api import sync_playwright
from scraper.base import RawItem, save_items
from config.settings import RAW_DIR


def scrape_product_hunt() -> list[RawItem]:
    """抓取 Product Hunt 首页今日产品"""
    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        # 隐藏自动化标记
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
        """)

        try:
            page.goto("https://www.producthunt.com/", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            # Product Hunt 使用 data-test 属性标记产品卡片
            # 首页产品列表区域
            cards = page.query_selector_all("[data-test^='post-item']")

            # 如果 data-test 选择器没命中，尝试备选选择器
            if not cards:
                cards = page.query_selector_all(".styles_item__Dk_nz, [class*='post-item'], [class*='PostItem']")

            # 再试一种：直接找产品链接
            if not cards:
                links = page.query_selector_all("a[href^='/posts/']")
                for link in links[:20]:
                    title = link.inner_text().strip()
                    href = link.get_attribute("href") or ""
                    if title and len(title) > 5:
                        full_url = f"https://www.producthunt.com{href}" if not href.startswith("http") else href
                        item = RawItem(
                            source="product_hunt",
                            title=title,
                            source_url=full_url,
                            author="Product Hunt",
                        )
                        if item.is_valid():
                            items.append(item)
                browser.close()
                return items

            for card in cards[:20]:
                # 提取标题
                title_el = card.query_selector("a[data-test='post-name'], h3, [class*='title']")
                # 提取描述
                desc_el = card.query_selector("[data-test='post-tagline'], [class*='tagline'], p")
                # 提取链接
                link_el = card.query_selector("a[href^='/posts/']")

                title = title_el.inner_text().strip() if title_el else ""
                summary = desc_el.inner_text().strip() if desc_el else ""
                href = link_el.get_attribute("href") if link_el else ""

                if href and not href.startswith("http"):
                    href = f"https://www.producthunt.com{href}"

                item = RawItem(
                    source="product_hunt",
                    title=title,
                    summary=summary,
                    source_url=href,
                    author="Product Hunt",
                )
                if item.is_valid():
                    items.append(item)

        except Exception as e:
            print(f"  [product_hunt] Error: {e}")
        finally:
            browser.close()

    return items


def run():
    """执行抓取并保存"""
    print("  [product_hunt] Scraping...")
    items = scrape_product_hunt()
    if items:
        save_items(items, "product_hunt", RAW_DIR)
    else:
        print("  [product_hunt] No items scraped, falling back to RSS")
    return items


if __name__ == "__main__":
    run()
