# 快速打开简报网页

## 交付给用户时

1. **确认文件存在**：`web/dist/briefing/{DATE}.html`（`{DATE}` 为 `YYYY-MM-DD`）。
2. **用系统默认浏览器打开**（项目根目录执行）：
   - macOS：`open web/dist/briefing/{DATE}.html`
   - Windows：`start web\dist\briefing\{DATE}.html`
   - 通用：在 Cursor / 资源管理器中双击该 `.html`。
3. **说明**：页面依赖 `web/dist/static/briefing.css`（由构建从 skill `assets/briefing.css` 复制）；勿只拷贝单个 HTML 而不带 `static` 目录。

## 若样式丢失（纯文本感）

- 检查 `web/dist/static/briefing.css` 是否存在。
- 重新运行：`python tools/briefing_to_html.py {DATE}` 或 `python .claude/skills/briefing-html-style/scripts/build_briefing_html.py {DATE}`。

## 若页面是旧的

- 改的是 `data/output/*-briefing.md` 而未重跑转换 → 执行上述补生成命令或完整 `python -m pipeline.main`。
