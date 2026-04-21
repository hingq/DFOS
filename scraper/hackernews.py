"""Hacker News 抓取（AI/设计相关）

Hacker News 的 DOM 结构极其稳定（十几年没怎么变过），
是最容易抓取的网站之一。使用 Algolia API 按关键词过滤。
"""
from playwright.sync_api import sync_playwright
from scraper.base import RawItem, save_items
from config.settings import RAW_DIR


# HN 搜索 API（Algolia），比抓页面更稳定
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"

# 搜索关键词：AI × 设计交叉领域
SEARCH_QUERIES = [
    "AI design tool",
    "AI UX",
    "Figma AI",
    "Cursor AI",
    "v0 Vercel",
    "AI product design",
    "LLM UI",
]


def scrape_hn_page() -> list[RawItem]:
    """直接抓取 HN 首页（备选方案，DOM 非常稳定）"""
    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://news.ycombinator.com/", wait_until="networkidle", timeout=15000)

            # HN 的 DOM 十几年如一日地稳定
            rows = page.query_selector_all("tr.athing")

            for row in rows[:30]:
                # 标题和链接
                title_el = row.query_selector("td.title > span.titleline > a")
                if not title_el:
                    continue

                title = title_el.inner_text().strip()
                href = title_el.get_attribute("href") or ""

                # HN 内部链接补全
                if href.startswith("item?"):
                    href = f"https://news.ycombinator.com/{href}"

                # 获取分数（在下一行 tr 里）
                score_row = row.evaluate_handle("el => el.nextElementSibling")
                score = ""
                if score_row:
                    try:
                        score_el = score_row.query_selector(".score")
                        if score_el:
                            score = score_el.inner_text().strip()
                    except:
                        pass

                item = RawItem(
                    source="hackernews",
                    title=title,
                    summary=f"HN {score}" if score else "",
                    source_url=href,
                    author="Hacker News",
                )
                if item.is_valid():
                    items.append(item)

        except Exception as e:
            print(f"  [hackernews] Error: {e}")
        finally:
            browser.close()

    return items


def run():
    """执行抓取并保存"""
    print("  [hackernews] Scraping...")
    items = scrape_hn_page()
    if items:
        save_items(items, "hackernews", RAW_DIR)
    print(f"  [hackernews] Got {len(items)} items")
    return items


if __name__ == "__main__":
    run()
