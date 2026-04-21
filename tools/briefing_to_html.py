"""简报 Markdown → HTML。

- 样式 / 模板唯一源：`.claude/skills/briefing-html-style/assets/`（见 config.settings）
- 构建输出：`web/dist/briefing/{DATE}.html` + `web/dist/static/briefing.css`
- Agent 执行入口：`briefing-html-style/scripts/build_briefing_html.py`
"""
from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import markdown

from config.settings import (
    BRIEFING_HTML_CSS_SOURCE,
    BRIEFING_HTML_TEMPLATE,
    WEB_DIST_BRIEFING_DIR,
    WEB_DIST_STATIC_DIR,
)


def briefing_body_to_html_fragment(md_text: str) -> str:
    """Markdown 正文 → HTML 片段。"""
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )


def _page_title_from_md(md_text: str, date: str) -> str:
    """取首个一级标题作为浏览器标题，否则用默认。"""
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return f"情报日报 {date}"


def _load_shell_template() -> str:
    path = BRIEFING_HTML_TEMPLATE
    if not path.exists():
        raise FileNotFoundError(f"缺少简报模板: {path}")
    return path.read_text(encoding="utf-8")


def _sync_static_assets() -> None:
    """将 skill assets 中的样式复制到 dist，保证相对路径 `../static/briefing.css` 可用。"""
    src = BRIEFING_HTML_CSS_SOURCE
    if not src.exists():
        raise FileNotFoundError(f"缺少简报样式: {src}")
    WEB_DIST_STATIC_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, WEB_DIST_STATIC_DIR / "briefing.css")


def build_briefing_html(md_text: str, date: str) -> str:
    """返回完整 HTML 文档字符串。"""
    _sync_static_assets()
    body = briefing_body_to_html_fragment(md_text)
    body_indented = "\n".join(
        ("        " + line) if line.strip() else line
        for line in body.splitlines()
    )
    title = _page_title_from_md(md_text, date)
    shell = _load_shell_template()
    out = shell.replace("__TITLE__", html.escape(title))
    out = out.replace("__BODY__", body_indented.rstrip() + "\n")
    return out


def write_briefing_html(md_path: Path, date: str | None = None) -> Path:
    """读取 `*-briefing.md`，写入 `web/dist/briefing/{date}.html`。"""
    md_path = Path(md_path)
    text = md_path.read_text(encoding="utf-8")
    if date is None:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", md_path.stem)
        date = m.group(1) if m else md_path.stem
    WEB_DIST_BRIEFING_DIR.mkdir(parents=True, exist_ok=True)
    html_doc = build_briefing_html(text, date)
    out = WEB_DIST_BRIEFING_DIR / f"{date}.html"
    out.write_text(html_doc, encoding="utf-8")
    return out


def main() -> None:
    from datetime import datetime

    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    md = PROJECT_ROOT / "data" / "output" / f"{date}-briefing.md"
    if not md.exists():
        print(f"[briefing_to_html] 未找到: {md}")
        sys.exit(1)
    p = write_briefing_html(md, date)
    print(f"[briefing_to_html] 已写入 {p}")


if __name__ == "__main__":
    main()
