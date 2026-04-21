"""已弃用 shim：请改用 `python -m tools.tts_dialogue --preset audio-v2`。

旧版曾硬编码某日的 dialogue.md；统一入口改为默认读 `data/output/{DATE}-article.md`。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    print(
        "[tts] 本脚本已合并至统一入口: python -m tools.tts_dialogue --preset audio-v2",
        file=sys.stderr,
    )
    cmd = [
        sys.executable,
        "-m",
        "tools.tts_dialogue",
        "--preset",
        "audio-v2",
        *sys.argv[1:],
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
