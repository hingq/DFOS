"""从 `*-article.md` 解析 Q/A，讯飞分段合成并合并为单 MP3。"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[assignment]

from tools.tts_dialogue.merge_audio import filter_good_segments, merge_mp3_segments
from tools.tts_dialogue.parse import clean_segment_strip_role, parse_dialogues
from tools.tts_paths import article_md_path, audio_output_path, default_date

from tools.article_tts.xfyun_ws import synthesize_text_to_mp3, utf8_byte_chunks

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE entries when python-dotenv is unavailable."""
    if load_dotenv is not None:
        load_dotenv(path)
        return
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = _strip_env_cred(value)


def pick_vcn_q_a(speaker: str, vcn_q: str, vcn_a: str) -> str:
    """Q / Qearl → 男声 vcn，A → 女声 vcn（与 briefing-article-style 话轮一致）。"""
    u = speaker.strip().upper()
    if u == "Q" or u == "QEARL" or "QEARL" in u:
        return vcn_q
    if u == "A":
        return vcn_a
    return vcn_a


def _strip_env_cred(raw: str) -> str:
    """去掉首尾空白、BOM、ASCII/中文成对引号。"""
    s = raw.strip().strip("\ufeff")
    pairs = (
        ('"', '"'),
        ("'", "'"),
        ("\u201c", "\u201d"),
        ("\u2018", "\u2019"),
    )
    for a, b in pairs:
        if len(s) >= 2 and s.startswith(a) and s.endswith(b):
            s = s[len(a) : -len(b)].strip()
    return s


_load_env_file(_PROJECT_ROOT / ".env")


def load_xfyun_config() -> tuple[str, str, str, str, str]:
    app_id = _strip_env_cred(os.environ.get("XFYUN_APP_ID", ""))
    api_key = _strip_env_cred(os.environ.get("XFYUN_API_KEY", ""))
    api_secret = _strip_env_cred(os.environ.get("XFYUN_API_SECRET", ""))
    vcn_q = _strip_env_cred(os.environ.get("XFYUN_VCN_Q", "aisjiuxu"))
    vcn_a = _strip_env_cred(os.environ.get("XFYUN_VCN_A", "xiaoyan"))
    if not app_id or not api_key or not api_secret:
        print(
            "[article_tts] 请设置环境变量 XFYUN_APP_ID、XFYUN_API_KEY、XFYUN_API_SECRET",
            file=sys.stderr,
        )
        sys.exit(1)
    return app_id, api_key, api_secret, vcn_q, vcn_a


def synthesize_segment_files(
    segments: list[tuple[str, str]],
    seg_dir: Path,
    app_id: str,
    api_key: str,
    api_secret: str,
    vcn_q: str,
    vcn_a: str,
) -> list[Path]:
    paths: list[Path] = []
    for i, (speaker, raw) in enumerate(segments):
        text = clean_segment_strip_role(raw)
        if not text.strip():
            continue
        vcn = pick_vcn_q_a(speaker, vcn_q, vcn_a)
        sub_chunks = utf8_byte_chunks(text)
        if len(sub_chunks) == 1:
            out = seg_dir / f"seg_{i:04d}.mp3"
            data = synthesize_text_to_mp3(
                app_id, api_key, api_secret, sub_chunks[0], vcn
            )
            out.write_bytes(data)
            paths.append(out)
            print(f"  [{i+1}/{len(segments)}] {speaker} ({vcn}): {text[:48]}…")
        else:
            sub_paths: list[Path] = []
            for j, chunk in enumerate(sub_chunks):
                sub = seg_dir / f"seg_{i:04d}_p{j:02d}.mp3"
                sub.write_bytes(
                    synthesize_text_to_mp3(app_id, api_key, api_secret, chunk, vcn)
                )
                sub_paths.append(sub)
                time.sleep(0.2)
            merged = seg_dir / f"seg_{i:04d}.mp3"
            merge_mp3_segments(sub_paths, merged)
            for p in sub_paths:
                p.unlink(missing_ok=True)
            paths.append(merged)
            print(f"  [{i+1}/{len(segments)}] {speaker} ({vcn}) 多段合并: {text[:48]}…")
        time.sleep(0.25)
    return paths


def run_article_tts(date_str: str | None = None, output_stem: str = "dialogue-xfyun") -> Path:
    d = date_str or default_date()
    md_path = article_md_path(d)
    if not md_path.is_file():
        print(f"[article_tts] 未找到口播母本: {md_path}", file=sys.stderr)
        sys.exit(1)

    app_id, api_key, api_secret, vcn_q, vcn_a = load_xfyun_config()
    text = md_path.read_text(encoding="utf-8")
    matches = parse_dialogues(text)
    print(f"[article_tts] 输入: {md_path}")
    print(f"[article_tts] Q 音色 vcn={vcn_q}，A 音色 vcn={vcn_a}")
    print(f"[article_tts] 解析到 {len(matches)} 段对话")
    if not matches:
        print("[article_tts] 未解析到 **角色**: 段落，退出", file=sys.stderr)
        sys.exit(2)

    seg_dir = Path(tempfile.mkdtemp(prefix="dfos-article-tts-"))
    try:
        seg_paths = synthesize_segment_files(
            matches, seg_dir, app_id, api_key, api_secret, vcn_q, vcn_a
        )
        good, bad = filter_good_segments(seg_paths)
        print(f"[article_tts] 有效分段: {len(good)}，失败/过小: {len(bad)}")
        if not good:
            print("[article_tts] 没有可用分段", file=sys.stderr)
            sys.exit(3)
        final_out = audio_output_path(output_stem, d)
        merge_mode = merge_mp3_segments(good, final_out)
        print(f"[article_tts] 已写入: {final_out}")
        print(f"[article_tts] 合并方式: {merge_mode}")
        mb = final_out.stat().st_size / 1024 / 1024
        print(f"[article_tts] 约 {mb:.1f} MB")
        return final_out
    finally:
        for p in seg_dir.glob("*"):
            p.unlink(missing_ok=True)
        seg_dir.rmdir()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="article.md → 讯飞双音色口播 → 单文件 MP3",
    )
    p.add_argument(
        "--date",
        dest="date",
        default=None,
        help="YYYY-MM-DD（默认当天或 BRIEFING_DATE）",
    )
    p.add_argument(
        "--output-stem",
        default="dialogue-xfyun",
        help="输出 data/output/{DATE}-{stem}.mp3 的文件名中段",
    )
    args = p.parse_args(argv)
    run_article_tts(args.date, args.output_stem)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
