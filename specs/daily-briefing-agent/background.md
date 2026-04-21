# Background

## 任务定位

**Daily Briefing Agent** 负责将 **当日所有简报素材**（**Twitter 采集结果 + 其他信源爬取结果**）**合并**为同一数据流，经预过滤、LLM 评分、分类与实体提取，产出**唯一一份**当日 **简报 Markdown**（`briefing.md`）与中间 JSON。

**重要**：Twitter 与 RSS/HN/PH 等**不是两条独立的内容线**；二者**共同构成**「生成简报的资源池」，合流后只生成**一份**简报正文。`data/output/twitter/` 下的清单、KOL 等可作为**过程记录与溯源**，但不视为与 `briefing.md` 并列的另一套「日报」。

简报回答「今天发生了什么、编辑认为哪些值得看」，与 Part 2 的 **对话式长文 `article.md`** 分工不同：简报偏短讯列表与编辑视角；长文体裁由 Briefing Article Agent + `briefing-article-style` skill 约束。

## 素材合流

- **Twitter 渠道**：由 `twitter-intelligence-agent` 采集，应进入 `data/raw/` 或与 pipeline 约定的合并入口（以工程实现为准）。  
- **其他渠道**：`pipeline/main.py` 中的 rss、hackernews、producthunt、manual、autocli 等。  
- **产出**：`data/intermediate/{DATE}-scoring.json`、`data/intermediate/{DATE}-processing.json`、`data/output/{DATE}-briefing.md`。

## 与其他 Agent 的关系

- **并列供稿**：`twitter-intelligence-agent` 提供 Twitter 侧素材，与 scraper **合并**后由本 Agent 统一生成简报。  
- **下游**：`daily-briefing-article-agent` 读取 `processing.json`（及可选 `briefing.md`）生成 `article.md`。
