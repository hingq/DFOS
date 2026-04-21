# AI+Design Intelligence Platform

## 项目概述

AI + 设计行业情报平台。标准端到端流程为 **四步**，前一步的产出是后一步的输入（或前提）：

| 步骤 | 名称 | 核心产出 |
|------|------|----------|
| **1** | 数据抓取 | `data/raw/` 多信源 JSON；Twitter 侧辅助文件（如 `data/output/twitter/`） |
| **2** | 日报生成 | **一份** `briefing.md` + `processing.json` / `scoring.json`；同一步 **自动生成** 简报网页 `web/dist/briefing/{DATE}.html`（样式源：`briefing-html-style` 的 `assets/`） |
| **3** | 结构化文章 | 基于 `processing.json` **自动择一**（`pipeline/article_pick.py`），输出**对话式** `{DATE}-article.md` |
| **4** | 语音生成 | 仅基于第 3 步文字稿生成音频 |

---

## 四步流程（含 Agent 与 Skill）

### 步骤 1 — 数据抓取

**目标**：从多信源拉取原始条目，写入 `data/raw/{DATE}-*.json`；Twitter 内容与其它渠道**合流**为后续日报素材（不单独成一份「另一套日报」）。

**做什么**

- RSS、Hacker News、Product Hunt、manual、autocli 聚合页等（见 `pipeline/main.py`、`scraper/`、`config/sources.py`）。
- **Twitter/X**：由 **Twitter Intelligence** 执行（搜索、KOL、归档等），条目进入 raw 或辅助清单。

**关联 Agent**

| Agent | 说明 |
|--------|------|
| **twitter-intelligence-agent** | Twitter/X 情报采集、KOL、归档；产出供步骤 2 与其它 raw **合并** |
| （无独立「RSS Agent」） | RSS/PH/HN 等由 **scraper 模块** + **Daily Briefing** 主流程中的 `step_scrape` 统一调度 |

**关联 Skill**

| Skill | 用途 |
|-------|------|
| **autocli** | 需登录站点（含 Twitter/X）的抓取与浏览 |
| **multi-search**（可选） | 跨平台搜索、补抓页面，用于扩充步骤 1 或步骤 3 素材 |

**典型指令 / 入口**

- `/twitter-intelligence` — 跑 Twitter Intelligence 约定产出  
- 主抓取：`python3 -m pipeline.main` 内的 `step_scrape`（或拆步执行时先保证 raw 齐全）

---

### 步骤 2 — 日报生成

**目标**：把**步骤 1 的全部抓取信息**合入同一 pipeline，经预过滤 → 评分 → 分类与实体提取 → **生成唯一简报**。

**产出**

- `data/intermediate/{DATE}-scoring.json`
- `data/intermediate/{DATE}-processing.json`
- `data/output/{DATE}-briefing.md`（Markdown 主稿；在「今日摘要」后可有 **`## 值得深挖`** 0～2 条，规则见 `context/deep_dive.md`，数据来自 `processing.json` + `pipeline/deep_dive.py` 频次合并）
- `web/dist/briefing/{DATE}.html` + `web/dist/static/briefing.css`（由 `tools/briefing_to_html.py` 读取 `.claude/skills/briefing-html-style/assets/`，与 `briefing.md` **同步生成**；**勿**在 `data/output/` 维护 HTML）

**关联 Agent**

| Agent | 说明 |
|--------|------|
| **daily-briefing-agent** | 对应 `pipeline.main`：`prefilter` → `scoring` → `processing` → `generation`（简报正文） |

**关联 Skill**

| Skill | 用途 |
|-------|------|
| **daily-review** | 用户说「审核日报」等：跑 `review-checker.py`，检查排序、tier、长度等 |
| **briefing-html-style** | 简报**网页**版式、打开 `web/dist/...html`、手改 md 后补生成；模板/CSS 在 skill `assets/` |

**典型指令**

- `/daily-briefing` 或 `python3 -m pipeline.main`（Step 3 内自动写 `web/dist/briefing/{DATE}.html`，失败则日志 `[briefing] HTML 跳过`）
- 仅补网页：`python3 tools/briefing_to_html.py [YYYY-MM-DD]` 或 `python3 .claude/skills/briefing-html-style/scripts/build_briefing_html.py [DATE]`

**说明**：Twitter 与 RSS 等在 **评分与展示权重** 上已可通过 `source_channel`、`config/settings.py`（如 `TWITTER_PREFILTER_BOOST`）等配置影响简报；详见 `pipeline/prompts/scoring.py`。

---

### 步骤 3 — 结构化文章（单产品 · 对话式 · 全量分析）

**目标**：从步骤 2 的 **`processing.json` / `briefing.md` 中选定「当日最值得做深度分析的 1 个 AI 产品/工具」**，做**全量分析**（能力、边界、对设计/产品工作流的影响、争议点等），体裁为**对话式长文**，且为**唯一口播母本**。

**产出**

- `data/output/{DATE}-article.md`（对话式结构；**非**与简报平行的第二套短讯列表）

**选题逻辑（概要）**

- 代码实现：`pipeline/article_pick.py`（优先 `category=new_tool`，再 `tier`，再 `final_score`）。  
- 体裁与人工改稿：见 `specs/daily-briefing-article-agent/` 与 **briefing-article-style** skill；`expectations.md` 用于论述深度而非自动打分。

**关联 Agent**

| Agent | 说明 |
|--------|------|
| **daily-briefing-article-agent**（Briefing Article） | 读取 `processing.json`（及可选 `briefing.md`），生成对话式 `article.md` |
| **product-research-agent**（可选） | 对选定产品做补充调研，**素材汇入** `article.md`，不单独再写一篇平行长文 |

**关联 Skill**

| Skill | 用途 |
|-------|------|
| **briefing-article-style** | 对话结构、角色、篇幅、与 `context/` 对齐；**生成或改稿 `article.md` 时必引用** |
| **multi-search**（可选） | 外源观点、竞品信息，供全量分析引用（须区分事实与二手观点） |

**典型指令**

- `/briefing-article` 或 `python3 -m tools.generate_article [--date YYYY-MM-DD]`

**Context 建议**

- `expectations.md`、`viewpoint.md`、`style.md`、`excellent.md` 等（由 `load_context()` 或 skill 显式引用）

---

### 步骤 4 — 语音生成

**目标**：仅针对步骤 3 的**文字稿** `{DATE}-article.md` 生成音频，**不再**从 `briefing.md` 单独写一篇对话再录。

**产出**

- `data/output/{DATE}-dialogue-xfyun.mp3`（讯飞）或 `{DATE}-dialogue-*.mp3`（`tts_dialogue` preset，以 `specs/dialogue-briefing-agent/output.md` 为准）

**关联 Agent**

| Agent | 说明 |
|--------|------|
| **dialogue-briefing-agent** | **仅音频**：输入 = `article.md`，输出 = TTS 音频 |

**关联 Skill**

| Skill | 用途 |
|-------|------|
| **article-dialogue-tts** | 讯飞整篇口播：`python -m tools.article_tts`；备选 `tools.tts_dialogue`（Edge） |

**典型指令**

- `/dialogue-briefing`

---

## 总流程图（四步）

```
┌── 1. 数据抓取 ─────────────────────────────────────────────┐
│  RSS / HN / PH / manual / autocli…  +  Twitter Intelligence  │
│  → data/raw/ …  （Twitter 辅助文件可写 data/output/twitter/） │
└────────────────────────────┬─────────────────────────────────┘
                           ↓
┌── 2. 日报生成（daily-briefing-agent）───────────────────────┐
│  全部 raw 合流 → prefilter → scoring → processing          │
│  → briefing.md + processing.json + web/dist/...html         │
└────────────────────────────┬─────────────────────────────────┘
                           ↓
┌── 3. 结构化文章（briefing-article-agent + skill）───────────┐
│  择 1 个最值得分析的 AI 产品 → 对话式全量分析                 │
│  → article.md（口播母本）  [可选: product-research / multi-search] │
└────────────────────────────┬─────────────────────────────────┘
                           ↓
┌── 4. 语音（dialogue-briefing-agent + article-dialogue-tts）──┐
│  article.md → *.mp3（主：讯飞 article_tts；备选 tts_dialogue）│
└─────────────────────────────────────────────────────────────┘
```

---

## Agent 数据流（简图）

```
[步骤1 抓取] → raw（+ twitter 辅助）
       ↓
[步骤2 daily-briefing-agent] → briefing.md + processing.json + web/dist/briefing/{DATE}.html
       ↓
[步骤3 briefing-article-agent] → article.md（单产品 · 对话式）
       ↓
[步骤4 dialogue-briefing-agent] → 音频
```

---

## Agent Specs 目录

```
specs/
├── twitter-intelligence-agent/
├── daily-briefing-agent/
├── daily-briefing-article-agent/
├── dialogue-briefing-agent/
├── product-research-agent/        # 产品调研档案（步骤 3 可选素材）
└── （competitive-analysis 见 .claude/commands/）
```

**步骤 3 选题**：`pipeline/article_pick.py`（由 `tools/generate_article.py` 调用）。

执行任一 agent 前：**先读满该目录下 spec**，勿在执行中改 spec。

---

## Commands 速查

| 指令 | 对应步骤 | 说明 |
|------|----------|------|
| `/twitter-intelligence` | 1 | Twitter 采集 |
| `/daily-briefing` | 2 | 日报 pipeline |
| `/briefing-article` | 3 | 对话式 `article.md` |
| `/dialogue-briefing` | 4 | `article.md` → 音频 |
| `/review-briefing` | 2 质检 | 配合 **daily-review** skill |
| `/product-research` | 3 可选 | 产品补充调研 |

---

## 核心规则

1. **步骤 1 + 2**：抓取内容**全部**进入日报 pipeline；简报只有**一份** Markdown 正文 `briefing.md`；其 **HTML 展示**在 `web/dist/briefing/`，**不**把可维护 HTML 放进 `data/output/`。  
2. **步骤 3**：**一篇** `article.md`，聚焦**一个**最值得分析的 AI 产品，**对话式全量分析**；风格由 **briefing-article-style** skill 约束。  
3. **步骤 4**：**只读** `article.md` 出语音，不另写第二份长对话稿。  
4. **Prompt**：勿随意改 `scoring.py` 权重；`generation.py` 用 `load_context()`。

---

## Skills 总表

| Skill | 路径 | 主要步骤 |
|-------|------|----------|
| **briefing-article-style** | `.claude/skills/briefing-article-style/` | **3** |
| **autocli** | `.claude/skills/autocli/` | **1** |
| **multi-search** | `.claude/skills/multi-search/` | **1**（可选）**3**（可选） |
| **daily-review** | `.claude/skills/daily-review/` | **2** |
| **briefing-html-style** | `.claude/skills/briefing-html-style/` | **2**（简报网页、`web/dist/`） |
| **article-dialogue-tts** | `.claude/skills/article-dialogue-tts/` | **4** |

---

## 技术栈与目录

- Python 3.11+，Anthropic Claude API，Playwright，feedparser  
- `config/`、`context/`、`pipeline/prompts/`、`scraper/`、`tools/`、`data/` 见各子目录说明

---

## Docs

| 文件 | 用途 |
|------|------|
| `docs/run-pipeline-guide.md` | 四步流程、命令、排错 |
| `docs/e2e-test-checklist.md` | 端到端测试清单 |
| `scripts/daily-briefing.sh` | 日报 pipeline 编排入口 |
| `docs/prompt-tuning-guide.md` | prompt 迭代 |
| `docs/prompt-changelog.md` | 变更记录 |
| `docs/review-log.md` | 审核记录 |

---

## TTS 配置（步骤 4）

- **主入口（讯飞）**：`python -m tools.article_tts [--date YYYY-MM-DD]`；环境变量 **`XFYUN_APP_ID`、`XFYUN_API_KEY`、`XFYUN_API_SECRET`**；可选 **`XFYUN_VCN_Q` / `XFYUN_VCN_A`**（Q 男、A 女）。默认读 **`data/output/{DATE}-article.md`**，输出 **`{DATE}-dialogue-xfyun.mp3`**。详见 **`.claude/skills/article-dialogue-tts/`**。  
- **备选**：`python -m tools.tts_dialogue [--preset stereo|edge|…]`；`--list-presets` 查看预设（Edge 等，无需讯飞）。  
- 日期：当天或 **`BRIEFING_DATE`**；路径见 **`tools/tts_paths.py`**。  
- 旧 `tools/generate_dialogue_*.py` / `generate_audio_v*.py`（不含 **`generate_dialogue.py`** 文章生成器）为 **shim**。  
- 话轮：**`Q` 男声、`A` 女声**（与 `briefing-article-style` 一致）；历史标记 **`Qearl`** 按 Q 侧处理。

---

## 代码与 spec 对齐（待办时可查）

- `tools/generate_article.py` 宜与 **单产品对话式全量分析** + **briefing-article-style** 一致。
