"""TTS 脚本共用路径：默认读取 data/output/{DATE}-article.md。

日期优先级：环境变量 BRIEFING_DATE（YYYY-MM-DD）> 当天日期。
整篇分角色口播主路径：`python -m tools.article_tts`（讯飞）；备选 `python -m tools.tts_dialogue`。
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def default_date() -> str:
    return os.environ.get("BRIEFING_DATE") or datetime.now().strftime("%Y-%m-%d")


def article_md_path(date_str: str | None = None) -> Path:
    """口播母本：{DATE}-article.md"""
    d = date_str or default_date()
    return OUTPUT_DIR / f"{d}-article.md"


def audio_output_path(stem_suffix: str, date_str: str | None = None) -> Path:
    """例如 stem_suffix='dialogue-noiz' -> {DATE}-dialogue-noiz.mp3"""
    d = date_str or default_date()
    return OUTPUT_DIR / f"{d}-{stem_suffix}.mp3"
