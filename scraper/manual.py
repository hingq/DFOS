"""手动输入合并

将 data/manual/ 目录下的手动添加条目合并进当天的原始数据。
"""
import json
from datetime import datetime
from scraper.base import RawItem, save_items
from config.settings import MANUAL_DIR, RAW_DIR


def run() -> list[RawItem]:
    """加载今天的手动输入"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = MANUAL_DIR / f"{date_str}.json"

    if not filepath.exists():
        print("  [manual] No manual items for today")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = []
    for entry in data:
        item = RawItem(
            source="manual",
            title=entry.get("title", ""),
            source_url=entry.get("source_url", ""),
            summary=entry.get("summary", ""),
            scraped_at=entry.get("scraped_at", datetime.now().isoformat()),
        )
        if item.is_valid():
            items.append(item)

    if items:
        save_items(items, "manual", RAW_DIR)

    print(f"  [manual] Loaded {len(items)} manual items")
    return items


if __name__ == "__main__":
    run()
