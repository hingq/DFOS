#!/usr/bin/env python3
"""简报 Markdown → HTML（执行入口）。

从本 skill 的 `assets/` 读模板与 CSS，写入 `web/dist/`。
委托 `tools.briefing_to_html`，须在项目根上下文运行。

用法（项目根）:
  python .claude/skills/briefing-html-style/scripts/build_briefing_html.py [YYYY-MM-DD]
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# DFOS 项目根：…/briefing-html-style/scripts → parents[4]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.briefing_to_html import write_briefing_html  # noqa: E402


def main() -> None:
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    md = PROJECT_ROOT / "data" / "output" / f"{date}-briefing.md"
    if not md.exists():
        print(f"[build_briefing_html] 未找到: {md}")
        sys.exit(1)
    p = write_briefing_html(md, date)
    print(f"[build_briefing_html] 已写入 {p}")


if __name__ == "__main__":
    main()
