#!/usr/bin/env python3
"""article.md → 讯飞口播 MP3（执行入口）。

须在 DFOS 项目根目录运行；委托 `tools.article_tts`。

用法:
  python .claude/skills/article-dialogue-tts/scripts/synthesize_article.py [--date YYYY-MM-DD]
"""
from __future__ import annotations

import sys
from pathlib import Path

# DFOS 项目根：…/article-dialogue-tts/scripts → parents[4]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.article_tts.runner import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
