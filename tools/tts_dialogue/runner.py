"""执行预设：解析 → 分段合成 → 合并。"""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

from tools.tts_paths import article_md_path, audio_output_path, default_date

from tools.tts_dialogue.backends import edge_backend, noiz_http, noiz_subprocess
from tools.tts_dialogue.merge_audio import (
    filter_good_segments,
    merge_mp3_segments,
    merge_moviepy,
)
from tools.tts_dialogue.parse import (
    clean_segment_simple,
    clean_segment_strip_role,
    parse_dialogues,
)
from tools.tts_dialogue.prefixes import PREFIX_REGISTRY
from tools.tts_dialogue.presets import PRESETS, DialoguePreset


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _clean(mode: str, text: str) -> str:
    if mode == "simple":
        return clean_segment_simple(text)
    return clean_segment_strip_role(text)


def _pick_voice(preset: DialoguePreset, speaker: str) -> str:
    """Q / Qearl → qearl_voice（男），A → lidada_voice（女）。"""
    u = speaker.strip().upper()
    if u == "Q" or u == "QEARL" or "QEARL" in u:
        return preset.qearl_voice
    if u == "A":
        return preset.lidada_voice
    return preset.lidada_voice


async def _run_edge_segments(
    preset: DialoguePreset,
    segments: list[tuple[str, str]],
    seg_dir: Path,
) -> list[Path]:
    paths_ordered: list[Path] = []
    for i, (speaker, raw) in enumerate(segments):
        prefix_fn = PREFIX_REGISTRY[preset.prefix_key]
        text = prefix_fn(i, speaker, _clean(preset.clean_mode, raw))
        out = seg_dir / f"seg_{i:04d}.mp3"
        voice = _pick_voice(preset, speaker)
        try:
            await edge_backend.synthesize_segment(text, voice, out)
            print(f"  [{i+1}/{len(segments)}] {speaker}: {text[:40]}...")
        except Exception as e:
            if preset.continue_on_edge_error:
                print(f"  [tts] 跳过段 {i}: {e!s}"[:120])
                continue
            raise
        else:
            paths_ordered.append(out)
    return paths_ordered


def _run_noiz_cli_segments(
    preset: DialoguePreset,
    segments: list[tuple[str, str]],
    seg_dir: Path,
    root: Path,
) -> list[Path]:
    paths_ordered: list[Path] = []
    errors: list[tuple[int, str]] = []
    for i, (speaker, raw) in enumerate(segments):
        prefix_fn = PREFIX_REGISTRY[preset.prefix_key]
        text = prefix_fn(i, speaker, _clean(preset.clean_mode, raw))
        out = seg_dir / f"seg_{i:04d}.mp3"
        vid = _pick_voice(preset, speaker)
        r = noiz_subprocess.synthesize_segment(text, vid, out, root)
        if r.returncode != 0:
            err = (r.stderr or r.stdout or "")[:200]
            errors.append((i, err))
            print(f"  [tts] Noiz 错误 {i}: {err[:60]}...")
        elif not out.exists() or out.stat().st_size < 1000:
            errors.append((i, "file too small"))
            print(f"  [tts] 段 {i} 文件过小")
        else:
            print(f"  [{i+1}/{len(segments)}] {speaker}: {text[:40]}...")
        paths_ordered.append(out)
        if (i + 1) % 10 == 0:
            print(f"  … 已处理 {i+1}/{len(segments)}")
    if errors:
        print(f"  [tts] Noiz 失败段: {len(errors)}")
    return paths_ordered


async def _run_noiz_http_segments(
    preset: DialoguePreset,
    segments: list[tuple[str, str]],
    seg_dir: Path,
) -> list[Path]:
    paths_ordered: list[Path] = []
    for i, (speaker, raw) in enumerate(segments):
        prefix_fn = PREFIX_REGISTRY[preset.prefix_key]
        text = prefix_fn(i, speaker, _clean(preset.clean_mode, raw))
        out = seg_dir / f"seg_{i:04d}.mp3"
        vid = _pick_voice(preset, speaker)
        if i > 0:
            await asyncio.sleep(0.5)
        ok = await noiz_http.synthesize_segment(text, vid, out)
        if not ok:
            print(f"  [tts] 段 {i} HTTP 合成失败")
        else:
            print(f"  [{i+1}/{len(segments)}] {speaker}: {text[:40]}...")
        paths_ordered.append(out)
        if (i + 1) % 10 == 0:
            print(f"  … 已处理 {i+1}/{len(segments)}")
    return paths_ordered


def run_preset(preset_id: str, date_str: str | None = None) -> Path | None:
    """跑完整预设；返回合并后的 mp3 路径，若 merge=none 则返回 None。"""
    preset = PRESETS[preset_id]
    d = date_str or default_date()
    md_path = article_md_path(d)
    if not md_path.is_file():
        print(f"[tts] 未找到口播母本: {md_path}", file=sys.stderr)
        sys.exit(1)

    text = md_path.read_text(encoding="utf-8")
    matches = parse_dialogues(text)
    print(f"[tts] 输入: {md_path}")
    print(f"[tts] 预设: {preset.id} — {preset.description}")
    print(f"[tts] 解析到 {len(matches)} 段对话")

    if not matches:
        print("[tts] 未解析到 **角色**: 格式段落，退出", file=sys.stderr)
        sys.exit(2)

    root = _project_root()
    seg_dir = Path(tempfile.mkdtemp(prefix=f"dfos-tts-{preset.id}-"))

    final_out = audio_output_path(preset.output_stem, d)

    if preset.backend == "edge":
        seg_paths = asyncio.run(_run_edge_segments(preset, matches, seg_dir))
    elif preset.backend == "noiz_subprocess":
        seg_paths = _run_noiz_cli_segments(preset, matches, seg_dir, root)
    else:
        seg_paths = asyncio.run(_run_noiz_http_segments(preset, matches, seg_dir))

    good, bad = filter_good_segments(seg_paths)
    print(f"[tts] 有效分段: {len(good)}，过小或失败: {len(bad)}")

    if preset.merge == "none":
        print(f"[tts] 本预设不合并长文件；分段目录: {seg_dir}")
        print(f"[tts] 若需合并可改用 --preset stereo 或 edge 等")
        return None

    if not good:
        print("[tts] 没有可用分段，无法合并", file=sys.stderr)
        sys.exit(3)

    if preset.merge == "ffmpeg":
        try:
            merge_mode = merge_mp3_segments(good, final_out)
        except Exception as e:
            print(f"[tts] ffmpeg 合并失败: {e}", file=sys.stderr)
            sys.exit(4)
        print(f"[tts] 已写入: {final_out}")
        print(f"[tts] 合并方式: {merge_mode}")
        return final_out

    try:
        merge_moviepy(good, final_out)
    except Exception as e:
        print(f"[tts] moviepy 合并失败: {e}", file=sys.stderr)
        sys.exit(4)

    try:
        dur_sec = final_out.stat().st_size  # placeholder; old printed duration
        _ = dur_sec
    except OSError:
        pass
    print(f"[tts] 已写入: {final_out}")
    mb = final_out.stat().st_size / 1024 / 1024
    print(f"[tts] 约 {mb:.1f} MB")
    return final_out
