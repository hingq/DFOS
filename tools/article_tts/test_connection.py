"""测试讯飞 TTS websocket 连接，不生成最终音频文件。"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from tools.article_tts.xfyun_ws import synthesize_text_to_mp3

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def strip_env_cred(raw: str) -> str:
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


def load_dotenv_fallback(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = strip_env_cred(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="测试讯飞 TTS websocket 连接")
    parser.add_argument("--text", default="讯飞连接测试。", help="测试合成文本")
    parser.add_argument("--vcn", default=None, help="音色，默认读取 XFYUN_VCN_A")
    args = parser.parse_args(argv)

    load_dotenv_fallback(PROJECT_ROOT / ".env")

    app_id = strip_env_cred(os.environ.get("XFYUN_APP_ID", ""))
    api_key = strip_env_cred(os.environ.get("XFYUN_API_KEY", ""))
    api_secret = strip_env_cred(os.environ.get("XFYUN_API_SECRET", ""))
    vcn = strip_env_cred(args.vcn or os.environ.get("XFYUN_VCN_A", "xiaoyan"))

    missing = [
        name
        for name, value in (
            ("XFYUN_APP_ID", app_id),
            ("XFYUN_API_KEY", api_key),
            ("XFYUN_API_SECRET", api_secret),
        )
        if not value
    ]
    if missing:
        print(f"[xfyun-test] 缺少环境变量: {', '.join(missing)}", file=sys.stderr)
        return 1

    print(f"[xfyun-test] env ok; voice={vcn}")
    data = synthesize_text_to_mp3(app_id, api_key, api_secret, args.text, vcn)
    print(f"[xfyun-test] success; audio_bytes={len(data)}")
    if len(data) < 1000:
        print("[xfyun-test] 返回音频过小，请检查音色或接口响应", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
