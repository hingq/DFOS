"""对话口播 TTS：统一入口 `python -m tools.tts_dialogue`。

旧脚本 `tools/generate_dialogue_*.py`（除 `generate_dialogue.py` 文章生成器外）为 shim，转发至此。
"""

from __future__ import annotations

from tools.tts_dialogue.presets import PRESET_IDS

__all__ = ["PRESET_IDS"]
