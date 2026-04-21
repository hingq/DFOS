"""已弃用：原依赖仓库内 Noiz `tts.py` CLI。请改用 `python -m tools.article_tts`（讯飞）。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def resolve_tts_script(project_root: Path) -> Path:
    """保留函数签名；脚本已移除，触发明确错误提示。"""
    legacy = project_root / ".agents" / "skills" / "tts" / "scripts" / "tts.py"
    if legacy.is_file():
        return legacy
    raise FileNotFoundError(
        "Noiz TTS CLI 已随旧版 tts skill 移除。对话口播请使用："
        "python -m tools.article_tts（需讯飞密钥），"
        "或改用 --preset edge / stereo（Edge TTS，无需讯飞）。"
    )


def synthesize_segment(
    text: str,
    voice_id: str,
    output_file: Path,
    project_root: Path,
) -> subprocess.CompletedProcess[str]:
    script = resolve_tts_script(project_root)
    cmd = [
        sys.executable,
        str(script),
        "speak",
        "-t",
        text,
        "--voice-id",
        voice_id,
        "-o",
        str(output_file),
        "--backend",
        "noiz-guest",
    ]
    return subprocess.run(cmd, capture_output=True, text=True)
