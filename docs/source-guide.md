---
name: source-management
description: 信源管理流程。当用户说「加一个信源」「这个源不行」「评估信源质量」「信源健康度检查」时触发。执行信源新增、评估、降级操作，包括 RSS 验证和 Playwright 选择器编写。
---

# 信源管理 Skill

评估、新增、降级和移除信源。

## 触发条件

- 用户说「加一个信源」「添加 XXX 作为信源」
- 用户说「这个源不行」「移除 XXX」
- 用户说「信源健康度检查」「source review」
- 每周一次定期执行

## 工具依赖

- 文件编辑: `config/sources.py`
- 终端: 验证 RSS feed 可用性
- Playwright: 测试页面抓取选择器
- 文件读取: `data/intermediate/` 近 7 天的 scoring 数据

## 操作步骤

### 新增信源: RSS 类型

#### 步骤 1: 验证 RSS feed

```bash
# 测试 RSS 是否可访问、内容是否有效
python -c "
import feedparser
feed = feedparser.parse('RSS_URL_HERE')
print(f'Title: {feed.feed.get(\"title\", \"N/A\")}')
print(f'Entries: {len(feed.entries)}')
for e in feed.entries[:3]:
    print(f'  - {e.get(\"title\", \"\")}')
"
```

如果返回 0 条 → feed 地址错误或网站不支持 RSS。

#### 步骤 2: 添加到 sources.py

在 `config/sources.py` 对应分组中添加：

```python
{"name": "信源名", "type": "rss", "url": "RSS_URL", "enabled": True, "value": "一句话说明价值"},
```

#### 步骤 3: 测试运行

```bash
python -c "from scraper import rss; rss.run()"
cat data/raw/$(date +%Y-%m-%d)-rss.json | python -m json.tool | head -30
```

### 新增信源: Playwright 类型

#### 步骤 1: 用 Playwright Inspector 分析页面

```bash
playwright codegen TARGET_URL
```

在弹出的浏览器中点击：标题、摘要、链接。记录生成的选择器。

#### 步骤 2: 创建 scraper 文件

在 `scraper/` 下新建文件，参照以下模板：

```python
"""[信源名] 抓取"""
from playwright.sync_api import sync_playwright
from scraper.base import RawItem, save_items
from config.settings import RAW_DIR

def scrape() -> list[RawItem]:
    items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("TARGET_URL", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        cards = page.query_selector_all("CARD_SELECTOR")
        for card in cards[:20]:
            title_el = card.query_selector("TITLE_SELECTOR")
            summary_el = card.query_selector("SUMMARY_SELECTOR")
            link_el = card.query_selector("LINK_SELECTOR")
            item = RawItem(
                source="source_name",
                title=title_el.inner_text().strip() if title_el else "",
                summary=summary_el.inner_text().strip() if summary_el else "",
                source_url=link_el.get_attribute("href") or "" if link_el else "",
            )
            if item.is_valid():
                items.append(item)
        browser.close()
    return items

def run():
    print("  [source_name] Scraping...")
    items = scrape()
    if items:
        save_items(items, "source_name", RAW_DIR)
    return items
```

#### 步骤 3: 注册到 pipeline

在 `pipeline/main.py` 顶部添加 import，在 `step_scrape()` 中调用 `.run()`。

### 信源健康度检查

#### 步骤 1: 统计近 7 天数据

```bash
# 统计每个信源的表现
python -c "
import json, glob
from collections import Counter

files = sorted(glob.glob('data/intermediate/*-scoring.json'))[-7:]
source_stats = Counter()
source_passed = Counter()

for f in files:
    with open(f) as fh:
        items = json.load(fh)
    for item in items:
        src = item.get('source', 'unknown')
        source_stats[src] += 1
        if item.get('tier') != 'drop':
            source_passed[src] += 1

for src in sorted(source_stats):
    total = source_stats[src]
    passed = source_passed[src]
    rate = passed / total * 100 if total > 0 else 0
    print(f'{src}: {passed}/{total} ({rate:.0f}%)')
"
```

#### 步骤 2: 判断

```
信号率 > 20% → 健康，保留
信号率 5-20% → 观察，再跑一周
信号率 < 5% 连续 2 周 → 降级（enabled: False）
```

### 降级/移除信源

在 `config/sources.py` 中设置 `"enabled": False`。**不要删除配置**，保留记录。

在 `context/source.md` 记录降级原因。

## 关联文件

| 文件 | 用途 |
|------|------|
| `config/sources.py` | 信源配置 |
| `scraper/*.py` | 各信源抓取脚本 |
| `pipeline/main.py` | `step_scrape()` 注册入口 |
| `context/source.md` | 信源管理记录 |
