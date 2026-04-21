"""分段 mp3 合并：系统 ffmpeg、imageio-ffmpeg 或 moviepy。"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

MIN_BYTES = 1000


def filter_good_segments(paths: list[Path]) -> tuple[list[Path], list[Path]]:
    good: list[Path] = []
    bad: list[Path] = []
    for p in paths:
        if p.exists() and p.stat().st_size > MIN_BYTES:
            good.append(p)
        else:
            bad.append(p)
    return good, bad


def resolve_ffmpeg_exe() -> str | None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    try:
        import imageio_ffmpeg  # type: ignore
    except ImportError:
        return None
    return imageio_ffmpeg.get_ffmpeg_exe()


def merge_ffmpeg_concat(
    segment_paths: list[Path], output_mp3: Path, ffmpeg_exe: str = "ffmpeg"
) -> None:
    """无损拼接（与旧 `generate_dialogue_audio` 一致）。"""
    if not segment_paths:
        raise ValueError("无有效分段，无法合并")

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    ) as list_file:
        for p in segment_paths:
            # ffmpeg concat 需转义单引号
            ap = str(p.resolve()).replace("'", "'\\''")
            list_file.write(f"file '{ap}'\n")
        list_path = Path(list_file.name)

    try:
        subprocess.run(
            [
                ffmpeg_exe,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c",
                "copy",
                str(output_mp3),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        list_path.unlink(missing_ok=True)


def merge_mp3_segments(segment_paths: list[Path], output_mp3: Path) -> str:
    """合并 MP3，返回使用的合并方式。"""
    ffmpeg_exe = resolve_ffmpeg_exe()
    if not ffmpeg_exe:
        raise RuntimeError(
            "未找到 ffmpeg。请在当前 Python 环境安装 imageio-ffmpeg："
            "`python -m pip install imageio-ffmpeg`，或把 ffmpeg 加入 PATH。"
        )
    merge_ffmpeg_concat(segment_paths, output_mp3, ffmpeg_exe)
    if Path(ffmpeg_exe).name == "ffmpeg":
        return "ffmpeg"
    return "imageio-ffmpeg"


def merge_moviepy(segment_paths: list[Path], output_mp3: Path, fps: int = 44100) -> None:
    """需安装 moviepy。"""
    try:
        from moviepy.editor import AudioFileClip, concatenate_audioclips  # type: ignore
    except ImportError as e:
        raise RuntimeError("合并需要 moviepy：pip install moviepy") from e

    if not segment_paths:
        raise ValueError("无有效分段，无法合并")

    clips = [AudioFileClip(str(p)) for p in segment_paths]
    try:
        final = concatenate_audioclips(clips)
        final.write_audiofile(str(output_mp3), fps=fps, logger=None)
    finally:
        for c in clips:
            c.close()
