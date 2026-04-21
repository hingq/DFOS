"""已弃用 shim：请改用 `python -m tools.tts_dialogue --preset stereo`。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    print(
        "[tts] 本脚本已合并至统一入口: python -m tools.tts_dialogue --preset stereo",
        file=sys.stderr,
    )
    cmd = [sys.executable, "-m", "tools.tts_dialogue", "--preset", "stereo", *sys.argv[1:]]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
