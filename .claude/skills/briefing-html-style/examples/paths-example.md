# 路径示例（YYYY-MM-DD = 2026-04-21）

| 角色 | 路径 |
|------|------|
| Markdown 主稿 | `data/output/2026-04-21-briefing.md` |
| **应用打开的网页** | `web/dist/briefing/2026-04-21.html` |
| 构建复制的样式 | `web/dist/static/briefing.css` |
| **维护用样式 / 模板（唯一源）** | `.claude/skills/briefing-html-style/assets/briefing.css`、`assets/briefing_shell.html` |

一键打开（macOS，在项目根）：

```bash
open web/dist/briefing/2026-04-21.html
```

补生成（项目根）：

```bash
python .claude/skills/briefing-html-style/scripts/build_briefing_html.py 2026-04-21
```
