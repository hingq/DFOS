# 简报网页与流水线契约

## 每日自动化顺序（与 `pipeline.main` 一致）

1. **抓取**：素材入 `data/raw/`（可 `--skip-scrape` 复用当日 raw）。
2. **评分排序**：`step_score` — 预过滤 + LLM 六维打分 + `tier` 分层（`must_read` / `worth_noting` / `tool_radar`）。
3. **处理**：`step_process` — 分类、实体、`title`/`scoring_summary` 等与评分结果合并。
4. **生成简报 + 网页**：`step_generate` — LLM 写 `data/output/{DATE}-briefing.md`，随后 **同一函数内**调用 `write_briefing_html` → `web/dist/briefing/{DATE}.html`（失败则打 `[briefing] HTML 跳过`）。

因此：**排序之后**还会经过处理与正文生成，网页与最终简报 md **同时**落地；不是「仅排序完就写 HTML」。

## 单一事实源与分工

| 层级 | 路径 | 职责 |
|------|------|------|
| **主稿（编辑可改）** | `data/output/{DATE}-briefing.md` | 列表式/情报日报体 Markdown，prompt 见 `pipeline/prompts/generation.py` |
| **展示构建产物** | `web/dist/briefing/{DATE}.html` | **只由脚本生成**，不手改 |
| **样式与模板（维护）** | `.claude/skills/briefing-html-style/assets/briefing.css`、`assets/briefing_shell.html` | **唯一源**；改这里后需补跑构建 |

- **口播/TTS 母本**仍是 `data/output/{DATE}-article.md`（见 `briefing-article-style`）。

## 与代码对齐

| 行为 | 实现 |
|------|------|
| 跑完日报后顺带出 HTML | `pipeline/main.py` → `tools.briefing_to_html.write_briefing_html` |
| 仅 md 已存在、补出网页 | 项目根：`python tools/briefing_to_html.py YYYY-MM-DD` 或 `python .claude/skills/briefing-html-style/scripts/build_briefing_html.py YYYY-MM-DD` |
| 路径常量 | `config/settings.py`：`BRIEFING_HTML_TEMPLATE`、`BRIEFING_HTML_CSS_SOURCE`、`WEB_DIST_*` |

构建时将 **`assets/briefing.css` 复制**到 `web/dist/static/briefing.css`，保证 HTML 内 `../static/briefing.css` 在 `file://` 下可加载。

## 依赖

- Python 包：`markdown`（见 `requirements.txt`）
