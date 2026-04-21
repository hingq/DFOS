# 每日简报生成（步骤 1～2）

执行 **抓取素材合流 + 日报 pipeline**，产出 **`briefing.md`**（含条件输出的 **`## 值得深挖`** 0～2 条，见 `context/deep_dive.md`）、**`processing.json`**（含 `release_kind` / `anchor_*` / `deep_dive_fit` 等），并在 Step 3 **自动生成**与当日 `briefing.md` 同步的 **`web/dist/briefing/{DATE}.html`**（见 `briefing-html-style` skill）。  
**不**在本指令中生成 `article.md`（见 `briefing-article`）；**不**生成音频（见 `dialogue-briefing`）。

## 流程位置

| 步骤 | 产出 |
|------|------|
| 1 抓取 | `data/raw/*.json`（Twitter 与其它信源合流，见 `.claude/CLAUDE.md`） |
| 2 本指令 | `briefing.md`、`intermediate/*-processing.json`、`web/dist/briefing/{DATE}.html`（与 md 同步） |

## 推荐命令

```bash
# 完整抓取 + 处理（项目根目录）
./scripts/daily-briefing.sh

# 或
python -m pipeline.main
```

跳过抓取（仅重跑 LLM）：

```bash
python -m pipeline.main --skip-scrape
```

测试数据：

```bash
python -m tools.test_data
python -m pipeline.main --skip-scrape
```

详见 **`docs/run-pipeline-guide.md`**。

## 质量检查（可选）

```bash
python .claude/skills/daily-review/scripts/review-checker.py
```

若有 ⚠️：可在 `briefing.md` 中调整顺序或长度；严重问题记录到 `docs/prompt-changelog.md`。

## 第四步：输出结果

```bash
cat data/output/$(date +%Y-%m-%d)-briefing.md
open web/dist/briefing/$(date +%Y-%m-%d).html
# 第二行 macOS；其它系统见 briefing-html-style skill
```

并摘要：抓取条数、进评分池条数、最终进简报条数；**简报网页路径** `web/dist/briefing/{DATE}.html`。

## 约束

- 不要擅自修改 `pipeline/prompts/` 下 prompt（除非用户明确要求）
- 不要擅自修改 `config/`（除非用户明确要求）
- pipeline 报错时输出错误信息；所有产出写入 `data/`
