"""直接请求 Noiz Guest HTTP API（与旧 `generate_audio_v3` 行为一致）。"""
from __future__ import annotations

import asyncio
from pathlib import Path


async def synthesize_segment(
    text: str,
    voice_id: str,
    output_file: Path,
    *,
    retries: int = 3,
) -> bool:
    try:
        import aiohttp
    except ImportError as e:
        raise RuntimeError("audio-v3 预设需要 aiohttp") from e

    url = "https://noiz.ai/v1/tts/guest"
    is_chinese = any("\u4e00" <= c <= "\u9fff" for c in text)
    lang = "zh" if is_chinese else "en"

    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={
                        "text": text,
                        "voice_id": voice_id,
                        "format": "mp3",
                        "speed": 1.0,
                        "language": lang,
                    },
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        if len(content) > 500:
                            output_file.write_bytes(content)
                            return True
                        err = await resp.text()
                        raise RuntimeError(f"Invalid response: {err[:80]}")
                    if resp.status == 429:
                        wait_time = 20 + attempt * 5
                        print(f"  [tts] Rate limited, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    err = await resp.text()
                    raise RuntimeError(f"API error {resp.status}: {err[:80]}")
        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                wait_time = 20 + attempt * 5
                print(f"  [tts] Rate limited, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            raise
    return False
