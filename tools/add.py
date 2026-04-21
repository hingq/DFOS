"""手动添加条目工具

用法:
  python -m tools.add "标题" "https://url" "推荐理由"
  python -m tools.add "Figma 发布 AI 新功能" "https://figma.com/blog/..." "直接影响设计工作流"
"""
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import MANUAL_DIR


def add_item(title: str, url: str = "", reason: str = ""):
    """添加一条手动条目到明天的队列"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    filepath = MANUAL_DIR / f"{tomorrow}.json"

    entry = {
        "source": "manual",
        "title": title,
        "source_url": url,
        "summary": reason,
        "scraped_at": datetime.now().isoformat(),
    }

    # 追加到文件
    items = []
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            items = json.load(f)

    items.append(entry)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"✓ Added to {filepath.name}: {title}")
    print(f"  URL: {url or '(none)'}")
    print(f"  Reason: {reason or '(none)'}")
    print(f"  Total items for {tomorrow}: {len(items)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m tools.add <title> [url] [reason]")
        print('Example: python -m tools.add "Figma AI update" "https://..." "重大功能更新"')
        sys.exit(1)

    title = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else ""
    reason = sys.argv[3] if len(sys.argv) > 3 else ""

    add_item(title, url, reason)


if __name__ == "__main__":
    main()
