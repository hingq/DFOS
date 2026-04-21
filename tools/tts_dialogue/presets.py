"""预设：与旧 `tools/generate_dialogue_*.py` / `generate_audio_v*.py` 行为对齐。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Backend = Literal["edge", "noiz_subprocess", "noiz_http"]
CleanMode = Literal["simple", "strip_role"]
MergeMode = Literal["none", "ffmpeg", "moviepy"]


@dataclass(frozen=True)
class DialoguePreset:
    """单套口播参数。"""

    id: str
    description: str
    backend: Backend
    output_stem: str
    qearl_voice: str
    lidada_voice: str
    clean_mode: CleanMode
    prefix_key: str
    merge: MergeMode
    continue_on_edge_error: bool = False


PRESETS: dict[str, DialoguePreset] = {
    "stereo": DialoguePreset(
        id="stereo",
        description="Edge Yunxi + Xiaoxiao，ffmpeg 合并（旧 generate_dialogue_audio）",
        backend="edge",
        output_stem="dialogue-stereo",
        qearl_voice="zh-CN-YunxiNeural",
        lidada_voice="zh-CN-XiaoxiaoNeural",
        clean_mode="simple",
        prefix_key="none",
        merge="ffmpeg",
    ),
    "stereo-xiaoyou": DialoguePreset(
        id="stereo-xiaoyou",
        description="Edge Yunxi + Xiaoyou，句首嗯/那个，不合并（旧 generate_dialogue_audio2）",
        backend="edge",
        output_stem="dialogue-stereo-xiaoyou",
        qearl_voice="zh-CN-YunxiNeural",
        lidada_voice="zh-CN-XiaoyouNeural",
        clean_mode="simple",
        prefix_key="audio2",
        merge="none",
    ),
    "stereo-prefixed": DialoguePreset(
        id="stereo-prefixed",
        description="Edge，句首那什么/那个，moviepy 合并→dialogue-stereo（旧 generate_dialogue_audio4）",
        backend="edge",
        output_stem="dialogue-stereo",
        qearl_voice="zh-CN-YunxiNeural",
        lidada_voice="zh-CN-XiaoxiaoNeural",
        clean_mode="strip_role",
        prefix_key="audio4",
        merge="moviepy",
        continue_on_edge_error=True,
    ),
    "edge": DialoguePreset(
        id="edge",
        description="Edge，稀疏句首，moviepy→dialogue-edge（旧 generate_dialogue_edge）",
        backend="edge",
        output_stem="dialogue-edge",
        qearl_voice="zh-CN-YunxiNeural",
        lidada_voice="zh-CN-XiaoxiaoNeural",
        clean_mode="strip_role",
        prefix_key="sparse_edge",
        merge="moviepy",
    ),
    "noiz": DialoguePreset(
        id="noiz",
        description="Noiz CLI guest，moviepy→dialogue-noiz（旧 generate_dialogue_noiz）",
        backend="noiz_subprocess",
        output_stem="dialogue-noiz",
        qearl_voice="ac09aeb4",
        lidada_voice="b4775100",
        clean_mode="strip_role",
        prefix_key="sparse_noiz",
        merge="moviepy",
    ),
    "noiz-guest": DialoguePreset(
        id="noiz-guest",
        description="Noiz CLI guest，moviepy→dialogue-guest（旧 generate_dialogue_audio3）",
        backend="noiz_subprocess",
        output_stem="dialogue-guest",
        qearl_voice="ac09aeb4",
        lidada_voice="b4775100",
        clean_mode="strip_role",
        prefix_key="guest_audio3",
        merge="moviepy",
    ),
    "audio-v2": DialoguePreset(
        id="audio-v2",
        description="Edge，无句首修饰，moviepy→dialogue-final（旧 generate_audio_v2，已改为读 article.md）",
        backend="edge",
        output_stem="dialogue-final",
        qearl_voice="zh-CN-YunxiNeural",
        lidada_voice="zh-CN-XiaoxiaoNeural",
        clean_mode="strip_role",
        prefix_key="none",
        merge="moviepy",
    ),
    "audio-v3": DialoguePreset(
        id="audio-v3",
        description="Noiz HTTP guest，moviepy→dialogue-final（旧 generate_audio_v3）",
        backend="noiz_http",
        output_stem="dialogue-final",
        qearl_voice="ac09aeb4",
        lidada_voice="a845c7de",
        clean_mode="strip_role",
        prefix_key="none",
        merge="moviepy",
    ),
}

PRESET_IDS: tuple[str, ...] = tuple(sorted(PRESETS.keys()))
