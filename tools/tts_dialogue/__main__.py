"""CLI：`python -m tools.tts_dialogue [--preset NAME] [--date YYYY-MM-DD]`。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.tts_dialogue.presets import PRESET_IDS, PRESETS
from tools.tts_dialogue.runner import run_preset


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="从 data/output/{DATE}-article.md 生成分角色口播音频（统一入口）",
    )
    parser.add_argument(
        "--preset",
        default="stereo",
        choices=sorted(PRESET_IDS),
        help="音色与合并策略（默认 stereo = Edge + ffmpeg）",
    )
    parser.add_argument(
        "--date",
        dest="date",
        default=None,
        help="日期 YYYY-MM-DD（默认当天或环境变量 BRIEFING_DATE）",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="列出预设说明并退出",
    )
    args = parser.parse_args(argv)

    if args.list_presets:
        for pid in sorted(PRESETS):
            p = PRESETS[pid]
            print(f"  {pid}")
            print(f"      {p.description}")
        return 0

    run_preset(args.preset, args.date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
