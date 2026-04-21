---
name: briefing-html-style
description: >-
  简报网页版：默认在每日 pipeline 中自动化生成——抓取合流、评分排序、分类处理、
  LLM 写出 briefing.md 之后，pipeline.main 的 Step 3 会立刻同步写出
  web/dist/briefing/{DATE}.html。版式与 HTML 骨架的唯一维护源在本 skill 的
  assets/（briefing.css、briefing_shell.html）。用户提到简报 HTML、情报日报网页、
  预览简报、打开 briefing、md 转 html、日报跑完看网页、web/dist、简报样式时
  务必使用本 skill。手改 md 后可执行 scripts/build_briefing_html.py 或
  tools/briefing_to_html.py。最终交付须给出可 open/双击的 HTML 路径。
  勿把可维护 HTML 放进 data/output。
---

# Briefing HTML Style（简报网页）

## 目录结构（与 Skill 规范对齐）

| 路径 | 用途 |
|------|------|
| `SKILL.md` | 唯一入口（本文件） |
| `assets/briefing.css` | **样式唯一源** |
| `assets/briefing_shell.html` | **页面骨架**（`__TITLE__` / `__BODY__`） |
| `scripts/build_briefing_html.py` | **可执行**：补生成 HTML（项目根相对路径） |
| `references/` | 流水线契约、快速打开说明 |
| `examples/` | 路径示例 |

## 何时使用

- **日报跑完后**：确认或打开已自动生成的 `web/dist/briefing/{DATE}.html`（主路径：`python -m pipeline.main`）
- 用户要 **预览 / 发布 / 打开**「情报日报」或列表式简报的 **网页版**
- 用户要 **改简报展示样式** → 只编辑 **`assets/briefing.css`** 或 **`assets/briefing_shell.html`**
- 用户**仅手改**了 `data/output/{DATE}-briefing.md`，要 **补生成 HTML**

## 与对话长文 skill 的分工

| 文件 | 用途 |
|------|------|
| `data/output/{DATE}-briefing.md` | 简报**正文主稿**（Markdown） |
| `web/dist/briefing/{DATE}.html` | 简报**只读展示页**，快速打开 |
| `data/output/{DATE}-article.md` | **口播/TTS 唯一母本**（见 `briefing-article-style`） |

## 核心流程

1. **路由**：任务涉及「简报网页、HTML、预览、打开、样式」而非写 `article.md` 对话稿 → 用本 skill。
2. **默认自动化（主路径）**：`python -m pipeline.main` 顺序为：**抓取 → 预过滤+评分排序 → 分类/实体处理 → Step 3 生成 `briefing.md` → 同一步内 `write_briefing_html`**。除非日志出现 `[briefing] HTML 跳过`，否则 `web/dist/briefing/{DATE}.html` 已更新。
3. **读入口**：流水线见 [references/pipeline-contract.md](references/pipeline-contract.md)。
4. **补生成（次路径）**（项目根）：
   - `python .claude/skills/briefing-html-style/scripts/build_briefing_html.py [YYYY-MM-DD]`
   - 或 `python tools/briefing_to_html.py [YYYY-MM-DD]`
5. **打开与验收**：[references/quick-open.md](references/quick-open.md)。
6. **改样式**：改 `assets/` 后执行上述补生成命令或整链 pipeline，以刷新 `web/dist`。

## 必须遵守（执行前扫一眼）

- **最终交付**：`web/dist/briefing/{DATE}.html` + `open`/双击说明；不要只贴未落盘的 HTML 字符串。
- **不要**在 `data/output/` 维护第二份简报 HTML；不要手写整页替代模板 + 构建脚本（除非用户明确要求）。
- **主稿以 Markdown 为准**；HTML 为派生物。
- 缺失 `markdown` 包时提示 `pip install -r requirements.txt`。

## 结构与版式（摘要）

- **版式源**：`assets/briefing.css`（**Notion 风格**：暖灰页底、白卡片、#37352f 正文、强调可点击链接样式）
- **骨架**：`assets/briefing_shell.html`（`article.briefing-prose` 包裹 Markdown 正文）
- **浏览器标题**：优先取自 md 首个 `#` 标题（`tools/briefing_to_html.py`）
- **正文约束**（由 `pipeline/prompts/generation.py` 约定）：每条资讯须有 Markdown 链接；**不含**「对训练营和课程的价值」类段落

## 深入阅读（按需打开）

| 文件 | 内容 |
|------|------|
| [references/pipeline-contract.md](references/pipeline-contract.md) | 路径、`config/settings`、`pipeline/main` |
| [references/quick-open.md](references/quick-open.md) | 打开方式、样式丢失排查 |
| [examples/paths-example.md](examples/paths-example.md) | 路径对照 |

## 自动化工具

| 工具 | 用法 |
|------|------|
| `python -m pipeline.main` | **主入口**：Step 3 自动写 md + `web/dist/...html` |
| `scripts/build_briefing_html.py` | **Skill 内脚本**：`python .claude/skills/briefing-html-style/scripts/build_briefing_html.py [DATE]` |
| `tools/briefing_to_html.py` | 同上逻辑，项目惯用入口 |

## 禁止

- 在 `web/static` 或已删除的旧路径维护样式（**已迁至 `assets/`**）。
- 用 **article.md** 替代 **briefing.md** 作为列表式简报网页内容源。
- 只口头让用户「自己拼 HTML」而不给出 **`web/dist` 下的真实路径**。
