# 运行 Pipeline 与四步流程

本文说明从 **数据抓取 → 日报 → 对话式 article → 语音** 的推荐命令与产物；与 `.claude/CLAUDE.md` 一致。

---

## 四步总览

| 步骤 | 命令要点 | 主要产出 |
|------|-----------|----------|
| 1 数据抓取 | Twitter Intelligence + `pipeline.main` 内 `step_scrape` | `data/raw/*.json` |
| 2 日报生成 | `python -m pipeline.main` | `briefing.md`、`processing.json`、`web/dist/briefing/{DATE}.html` |
| 3 结构化文章 | `python -m tools.generate_article` | `{DATE}-article.md` |
| 4 语音 | `BRIEFING_DATE=… python3 -m tools.article_tts`（讯飞）或 `tts_dialogue --preset edge` 等 | `{DATE}-dialogue-xfyun.mp3` 或 `{DATE}-dialogue-*.mp3` |

---

## 步骤 1～2：抓取 + 日报

### 推荐顺序

1. **Twitter Intelligence**（Claude 指令 `/twitter-intelligence` 或等价任务）将条目合入当日素材池，并尽量写入 `data/raw/` 或与工程约定一致的路径。  
2. 运行主 pipeline：

```bash
# 方式 A：项目脚本（含 PYTHONPATH 与提示）
./scripts/daily-briefing.sh

# 方式 B：直接调用
python -m pipeline.main
```

### 跳过抓取（仅重跑 LLM）

```bash
python -m pipeline.main --skip-scrape
```

### 使用测试数据

```bash
python -m tools.test_data
python -m pipeline.main --skip-scrape
```

### 产物

- `data/raw/YYYY-MM-DD-*.json`
- `data/intermediate/YYYY-MM-DD-scoring.json`
- `data/intermediate/YYYY-MM-DD-processing.json`
- `data/output/YYYY-MM-DD-briefing.md`
- `web/dist/briefing/YYYY-MM-DD.html`（与上同步；样式源 `.claude/skills/briefing-html-style/assets/`）

---

## 步骤 3：对话式 article（选题 + 生成）

选题由 **`pipeline/article_pick.py`** 从 `processing.json` 中选 **一条**（优先 `new_tool` + 高 `tier` + 高 `final_score`）。

```bash
python -m tools.generate_article
# 指定日期
python -m tools.generate_article --date 2026-04-20
# 或
BRIEFING_DATE=2026-04-20 python -m tools.generate_article
```

产出：`data/output/{DATE}-article.md`（口播母本）。

体裁约束：`.claude/skills/briefing-article-style/SKILL.md`。

---

## 步骤 4：TTS

输入默认为 **`data/output/{DATE}-article.md`**（见 `tools/tts_paths.py`）。

```bash
# 主路径：讯飞（需配置 XFYUN_APP_ID、XFYUN_API_KEY、XFYUN_API_SECRET）
BRIEFING_DATE=2026-04-20 python3 -m tools.article_tts --date 2026-04-20

# 备选：Edge 等（--list-presets 查看全部）
BRIEFING_DATE=2026-04-20 python3 -m tools.tts_dialogue --preset edge
```

Skill：`.claude/skills/article-dialogue-tts/SKILL.md`。

---

## 单独测试 scraper

```bash
python -c "from scraper import hackernews; hackernews.run()"
python -c "from scraper import producthunt; producthunt.run()"
python -c "from scraper import rss; rss.run()"
python -c "from scraper import autocli; autocli.run()"
ls -la data/raw/
```

---

## 手动加条

```bash
python -m tools.add "标题" "https://url" "推荐理由"
```

---

## 查看结果

```bash
cat data/output/$(date +%Y-%m-%d)-briefing.md
cat data/intermediate/$(date +%Y-%m-%d)-processing.json | python -m json.tool | head -80
cat data/output/$(date +%Y-%m-%d)-article.md | head -40
```

---

## 排错

| 现象 | 处理 |
|------|------|
| No raw items | 检查 `config/sources.py`、信源是否启用、是否已先跑 Twitter/测试数据 |
| JSON 解析失败 | 查看 `data/intermediate/`，缩小 `SCORING_POOL_SIZE` 或重试 |
| API key 错误 | 检查 `.env` 中 `MINIMAX_API_KEY`（须为 MiniMax 开放平台「接口密钥」，与 Anthropic 兼容网关 `https://api.minimax.io/anthropic` 匹配；401 `invalid api key` 多为密钥错误、已作废或账号类型不匹配） |
| article 报找不到 processing | 先完成步骤 2，或 `--date` 指向已有 intermediate 的日期 |

---

## 关联文件

| 文件 | 用途 |
|------|------|
| `pipeline/main.py` | 日报主入口 |
| `pipeline/article_pick.py` | 步骤 3 选题 |
| `tools/generate_article.py` | 步骤 3 成稿 |
| `tools/tts_paths.py` | TTS 输入路径 |
| `tools/test_data.py` | 测试 raw |
| `scripts/daily-briefing.sh` | 日报编排 shell |
| `docs/e2e-test-checklist.md` | 端到端测试清单 |
| `.env` | API key |
