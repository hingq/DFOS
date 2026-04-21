---
name: keyword-maintenance
description: 关键词维护流程。当用户说「加个关键词」「这个词应该在黑名单」「检查关键词」「keyword review」「为什么这条被过滤了」时触发。扫描被丢弃的内容检查误杀，更新白名单和黑名单。
---

# 关键词维护 Skill

维护预过滤层的白名单和黑名单关键词。

## 触发条件

- 用户说「加个关键词 XXX」「这个词该加白名单」
- 用户说「这个词应该在黑名单」
- 用户说「为什么这条被过滤了」
- 用户说「检查关键词」「keyword review」
- 每周一次定期执行

## 工具依赖

- 文件编辑: `config/keywords.py`, `config/blacklist.py`
- 终端: 运行预过滤测试

## 操作步骤

### 添加白名单关键词

#### 步骤 1: 确定维度

```
关键词属于哪个维度？

core (权重3x)    → AI×设计交叉：AI工具名、AI交互模式
product (权重2x) → 产品方法论：PMF、MVP、用户研究
design (权重2x)  → 体验设计：设计系统、交互设计、可用性
business (权重1.5x) → 商业增长：SaaS、融资、定价
tech (权重1x)    → 技术趋势：模型名、API、开源

不确定 → 默认放 tech（权重最低，影响最小）
```

#### 步骤 2: 编辑 keywords.py

在 `config/keywords.py` 对应列表中添加，中英文各一条：

```python
# 在对应的 WHITELIST_XXX 列表中添加
"新关键词英文", "新关键词中文",
```

#### 步骤 3: 验证

```bash
# 用今天的数据测试预过滤效果
python -c "
from scraper.base import load_all_raw
from pipeline.prefilter import prefilter
from config.settings import RAW_DIR
from datetime import datetime

items = load_all_raw(RAW_DIR, datetime.now().strftime('%Y-%m-%d'))
result = prefilter(items)
"
```

### 添加黑名单关键词

#### 步骤 1: 判断级别

```
硬黑名单（直接丢弃）:
  条件: 命中该词的内容 100% 无关，不会误伤
  示例: cryptocurrency, 自动驾驶, casino

软黑名单（降权不丢弃）:
  条件: 命中该词 80%+ 低质，但偶有例外
  示例: "10个AI工具", "入门指南", "press release"
```

#### 步骤 2: 编辑 blacklist.py

```python
# 硬黑名单 → BLACKLIST_HARD 列表
# 软黑名单 → BLACKLIST_SOFT 列表
```

### 每周关键词健康检查

#### 步骤 1: 扫描误杀

```bash
# 查看本周被硬黑名单丢弃的内容
python -c "
from scraper.base import load_all_raw
from config.blacklist import should_discard
from config.settings import RAW_DIR
from datetime import datetime

items = load_all_raw(RAW_DIR, datetime.now().strftime('%Y-%m-%d'))
for item in items:
    discard, reason = should_discard(item.get('title',''), item.get('summary',''))
    if discard:
        print(f'DISCARDED: {item[\"title\"][:60]} → {reason}')
"
```

检查输出：有没有被误杀的好内容？

#### 步骤 2: 扫描遗漏

```bash
# 查看白名单得分为 0 但进入了简报的条目
python -c "
from config.keywords import calculate_relevance
import json

with open('data/intermediate/$(date +%Y-%m-%d)-scoring.json') as f:
    items = json.load(f)
for item in items:
    if item.get('tier') != 'drop':
        score, matched = calculate_relevance(item.get('title',''), '')
        if score == 0:
            print(f'ZERO-SCORE IN BRIEFING: {item[\"title\"][:60]}')
            print(f'  → Consider adding keyword')
"
```

如果有零分条目进入简报 → 需要加新关键词。

## 原则

```
✅ 宁可漏加，不要多加（黑名单过度 = 好内容被误杀）
✅ 新工具名出现就加（AI 领域新词多）
✅ 中英文成对添加
❌ 不要频繁改权重（需要 2 周数据支撑）
```

## 关联文件

| 文件 | 用途 |
|------|------|
| `config/keywords.py` | 白名单和权重 |
| `config/blacklist.py` | 黑名单（硬+软）|
| `pipeline/prefilter.py` | 预过滤逻辑 |
