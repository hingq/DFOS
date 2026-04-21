"""抓取基类 — 定义统一的数据格式"""
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path


@dataclass
class RawItem:
    """统一的抓取结果格式"""
    source: str = ""
    source_url: str = ""
    title: str = ""
    summary: str = ""
    author: str = ""
    published_at: str = ""
    tags: list = field(default_factory=list)
    raw_text: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def is_valid(self) -> bool:
        return bool(self.title.strip())


def save_items(items: list[RawItem], source_name: str, output_dir: Path) -> Path:
    """保存抓取结果到 JSON 文件"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = output_dir / f"{date_str}-{source_name}.json"

    data = [item.to_dict() for item in items if item.is_valid()]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  [{source_name}] Saved {len(data)} items → {filepath.name}")
    return filepath


def load_all_raw(raw_dir: Path, date_str: str = None) -> list[dict]:
    """加载指定日期的所有原始数据"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    all_items = []
    for filepath in sorted(raw_dir.glob(f"{date_str}-*.json")):
        with open(filepath, "r", encoding="utf-8") as f:
            items = json.load(f)
            all_items.extend(items)

    return all_items
