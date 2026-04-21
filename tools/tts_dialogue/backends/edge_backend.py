"""Microsoft Edge TTS（edge_tts）。"""
from __future__ import annotations

from pathlib import Path


async def synthesize_segment(text: str, voice: str, output_file: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_file))
