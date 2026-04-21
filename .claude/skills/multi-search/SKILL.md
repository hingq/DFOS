---
name: multi-search
description: 多平台搜索与信息提取。支持 Bing、Google、Medium、Twitter/X、Product Hunt、Hacker News、少数派等平台。当用户说「搜索XXX」「搜一下」「去PH看看」「搜 Medium」「看看 HN」「Twitter 搜」「去少数派搜」「抓取这个页面」时触发。使用 Playwright MCP 插件打开目标页面并提取结构化结果。即使用户只是说"帮我查一下最近的AI设计工具"，也应该使用此 skill 执行搜索。
---

# 多平台搜索 Skill

在多个平台上搜索信息并提取结构化结果。一个脚本覆盖所有平台，自动识别页面类型。

## 触发条件

- 用户说「搜索 XXX」「搜一下 XXX」「web search」
- 用户说「去 Product Hunt 看看」「PH 上搜」
- 用户说「搜 Medium」「Medium 上有什么」
- 用户说「Twitter 搜 XXX」「X 上搜」
- 用户说「看看 Hacker News」「HN 有什么」
- 用户说「去少数派搜」「sspai 搜」
- 用户说「抓取这个页面的内容」
- 用户意图需要获取互联网最新信息

## 工具依赖

必须使用 Playwright MCP 插件 (`mcp__plugin_playwright_playwright__*`)。

核心脚本: `skills/multi-search/scripts/extract-results.js`

## 支持的平台

| 平台 | 搜索入口 URL | 结果类型 |
|------|-------------|---------|
| Bing | `https://www.bing.com` | 网页搜索结果 |
| Google | `https://www.google.com` | 网页搜索结果 |
| Medium | `https://medium.com/search?q=XXX` | 文章列表 |
| Twitter/X | `https://x.com/search?q=XXX` | 推文列表 |
| Product Hunt | `https://www.producthunt.com` | 今日产品 |
| Hacker News | `https://news.ycombinator.com` | 首页帖子 |
| 少数派 | `https://sspai.com` | 文章列表 |
| 任意页面 | 用户提供的 URL | 通用链接提取 |

---

## 操作步骤

### 场景 A: 搜索引擎搜索（Bing / Google）

#### 步骤 1: 打开搜索引擎

使用 `browser_navigate` 打开搜索引擎：

```
Bing: https://www.bing.com
Google: https://www.google.com
```

默认使用 Bing。用户明确指定 Google 时用 Google。

#### 步骤 2: 输入关键词并搜索

使用 `browser_type` 在搜索框输入关键词：

```
ref: 搜索框的 ref（从 snapshot 获取）
text: [关键词]
submit: true
```

#### 步骤 3: 等待结果加载

使用 `browser_wait_for_navigation` 或等待 2 秒。

#### 步骤 4: 提取结果

使用 `browser_evaluate` 执行提取脚本：

```javascript
// 读取并执行 skills/multi-search/scripts/extract-results.js
// 然后调用:
extractResults(15);
```

脚本会自动识别是 Bing 还是 Google，使用对应的提取逻辑。

#### 步骤 5: 翻页（如需要）

```javascript
// Bing 第 N 页
getBingPageUrl('关键词', 2)
// → https://www.bing.com/search?q=关键词&first=11

// Google 第 N 页
getGooglePageUrl('关键词', 2)
// → https://www.google.com/search?q=关键词&start=10
```

使用 `browser_navigate` 跳转后再次 `extractResults(15)`。

---

### 场景 B: Medium 搜索

#### 步骤 1: 直接用搜索 URL

```
https://medium.com/search?q=AI+design+tools
```

使用 `browser_navigate` 打开。

#### 步骤 2: 等待内容加载

Medium 是 SPA，需要等待：

```
browser_wait_for_selector: article, [data-testid="post-preview"]
timeout: 10000
```

#### 步骤 3: 提取结果

```javascript
extractResults(15);
```

---

### 场景 C: Twitter/X 搜索

#### 步骤 1: 直接用搜索 URL

```
https://x.com/search?q=AI+design&f=live
```

参数 `f=live` 表示按最新排序。

**注意**: Twitter 需要登录才能搜索。如果未登录，提示用户先登录。

#### 步骤 2: 等待内容加载

```
browser_wait_for_selector: [data-testid="tweet"]
timeout: 15000
```

#### 步骤 3: 滚动加载更多（可选）

```javascript
window.scrollBy(0, 2000);
// 等待 2 秒后再提取
```

#### 步骤 4: 提取结果

```javascript
extractResults(15);
```

---

### 场景 D: Product Hunt 今日产品

#### 步骤 1: 打开首页

```
https://www.producthunt.com
```

#### 步骤 2: 等待产品列表加载

```
browser_wait_for_selector: [data-test^="post-item"], a[href^="/posts/"]
timeout: 10000
```

#### 步骤 3: 提取结果

```javascript
extractResults(15);
```

---

### 场景 E: Hacker News

#### 步骤 1: 打开页面

```
首页: https://news.ycombinator.com
新帖: https://news.ycombinator.com/newest
搜索: https://hn.algolia.com/?q=AI+design
```

#### 步骤 2: 提取结果

Hacker News 页面极其简单，无需等待：

```javascript
extractResults(30);
```

---

### 场景 F: 少数派 (sspai.com)

#### 步骤 1: 打开页面

```
首页: https://sspai.com
搜索: https://sspai.com/search/post/AI
```

#### 步骤 2: 提取结果

```javascript
extractResults(15);
```

---

### 场景 G: 任意页面提取

用户给了一个具体 URL，想提取内容：

#### 步骤 1: 打开 URL

```
browser_navigate → 用户提供的 URL
```

#### 步骤 2: 提取结果

```javascript
extractResults(20);
```

脚本会使用通用提取策略（找所有 h1/h2/h3 中的链接）。

---

## 结果输出格式

提取完成后，将结果格式化返回给用户：

```markdown
## 搜索结果: [关键词] (来源: [平台])

### 1. [标题](URL)
- **来源**: 站点名
- **日期**: 日期
- 摘要内容...

### 2. [标题](URL)
- **来源**: 站点名
- 摘要内容...

---
共 N 条结果 | 平台: [platform] | [当前页码]
```

## 多平台联合搜索

当用户说「全网搜索 XXX」或需要综合多个来源时，按以下顺序搜索并合并结果：

1. Bing 搜索 → 获取 10 条通用结果
2. Product Hunt → 获取相关新产品
3. Hacker News → 获取技术社区讨论

每个平台的结果分组展示。

**执行流程**:
```
1. browser_navigate → bing.com → 搜索 → extractResults(10)
2. browser_navigate → producthunt.com → extractResults(10)
3. browser_navigate → news.ycombinator.com → extractResults(10)
4. 合并三组结果返回
```

## 为日报 Pipeline 采集内容

当用户说「采集今天的内容」「抓取信源」时，执行信源轮询：

```
1. browser_navigate → Hacker News → extractResults(30) → 保存
2. browser_navigate → Product Hunt → extractResults(15) → 保存
3. browser_navigate → Medium search "AI design" → extractResults(10) → 保存
4. 将所有结果合并保存到 data/raw/YYYY-MM-DD-browsed.json
```

保存脚本：

```python
import json
from datetime import datetime

def save_browsed_results(results, output_dir="data/raw"):
    date = datetime.now().strftime("%Y-%m-%d")
    filepath = f"{output_dir}/{date}-browsed.json"
    items = []
    for r in results:
        items.append({
            "source": r.get("platform", "unknown"),
            "title": r.get("title", ""),
            "summary": r.get("description", ""),
            "source_url": r.get("url", ""),
            "author": r.get("site", ""),
            "published_at": r.get("date", ""),
            "tags": [],
            "raw_text": "",
            "scraped_at": datetime.now().isoformat(),
        })
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return filepath
```

## 脚本文件

| 文件 | 用途 |
|------|------|
| `scripts/extract-results.js` | 多平台统一提取脚本 |

### extract-results.js 核心函数

| 函数 | 用途 |
|------|------|
| `extractResults(max)` | **主入口**: 自动识别平台并提取 |
| `detectPlatform()` | 自动识别当前页面类型 |
| `extractBing(max)` | Bing 搜索结果提取 |
| `extractGoogle(max)` | Google 搜索结果提取 |
| `extractMedium(max)` | Medium 文章提取 |
| `extractTwitter(max)` | Twitter/X 推文提取 |
| `extractProductHunt(max)` | Product Hunt 产品提取 |
| `extractHackerNews(max)` | Hacker News 帖子提取 |
| `extractSspai(max)` | 少数派文章提取 |
| `extractGeneric(max)` | 通用页面链接提取 |
| `getBingPageUrl(kw, page)` | Bing 翻页 URL |
| `getGooglePageUrl(kw, page)` | Google 翻页 URL |
| `getSearchKeyword()` | 获取当前搜索词 |

## 完整示例

**用户输入**: 「搜索 AI design tools，看看 Bing 和 Product Hunt 上有什么」

**执行流程**:
1. `browser_navigate` → `https://www.bing.com`
2. `browser_type` → 输入 "AI design tools"，回车
3. `browser_evaluate` → `extractResults(10)` 获取 Bing 结果
4. `browser_navigate` → `https://www.producthunt.com`
5. `browser_evaluate` → `extractResults(10)` 获取 PH 结果
6. 合并两组结果，格式化返回

**用户输入**: 「去 Medium 搜 AI UX 相关的文章」

**执行流程**:
1. `browser_navigate` → `https://medium.com/search?q=AI+UX`
2. 等待 `article` 元素加载
3. `browser_evaluate` → `extractResults(15)`
4. 格式化返回
