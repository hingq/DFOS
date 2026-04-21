"""科大讯飞在线语音合成流式 WebSocket API（v2）。

文档：https://www.xfyun.cn/doc/tts/online_tts/API.html
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from email.utils import formatdate
from urllib.parse import urlencode

try:
    import websocket
    from websocket._exceptions import WebSocketBadStatusException
except ImportError as e:
    websocket = None  # type: ignore[assignment]
    WebSocketBadStatusException = Exception  # type: ignore[misc, assignment]
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

WS_HOST = "tts-api.xfyun.cn"
WS_PATH = "/v2/tts"
WS_BASE = f"wss://{WS_HOST}{WS_PATH}"


def _websocket_sslopt() -> dict:
    """macOS 等环境下系统 CA 不全时，用 certifi 根证书做 wss 校验。"""
    try:
        import certifi

        return {"ca_certs": certifi.where()}
    except ImportError:
        return {}


def _require_ws() -> None:
    if websocket is None:
        raise RuntimeError(
            "需要安装 websocket-client：pip install websocket-client"
        ) from _IMPORT_ERROR


def assemble_ws_url(api_key: str, api_secret: str) -> str:
    """构造带鉴权 query 的 wss URL。"""
    # 必须用英文星期/月份（RFC 1123），避免 locale 影响 strftime
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    signature_origin = f"host: {WS_HOST}\ndate: {date}\nGET {WS_PATH} HTTP/1.1"
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode("utf-8")
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
        "utf-8"
    )
    params = {"authorization": authorization, "date": date, "host": WS_HOST}
    return WS_BASE + "?" + urlencode(params)


def synthesize_text_to_mp3(
    app_id: str,
    api_key: str,
    api_secret: str,
    text: str,
    vcn: str,
    *,
    speed: int = 50,
    volume: int = 50,
    pitch: int = 50,
) -> bytes:
    """单次会话合成一段文本，返回 MP3 二进制。"""
    _require_ws()
    if not text.strip():
        return b""
    url = assemble_ws_url(api_key, api_secret)
    try:
        ws = websocket.create_connection(
            url, timeout=120, sslopt=_websocket_sslopt()
        )
    except WebSocketBadStatusException as e:
        err = str(e)
        if "401" in err or "Unauthorized" in err:
            raise RuntimeError(
                "[article_tts] 讯飞握手 401：请核对开放平台该应用下「在线语音合成」的 "
                "APIKey（写入 XFYUN_API_KEY）与 APISecret（XFYUN_API_SECRET），"
                "勿与 AppID 混淆；并确认已开通流式合成能力。"
            ) from e
        if "403" in err and "IP address is not allowed" in err:
            raise RuntimeError(
                "[article_tts] 讯飞握手 403：当前出口 IP 不在讯飞应用允许列表中。"
                "请到讯飞开放平台该应用的在线语音合成/安全设置中加入当前公网 IP，"
                "或关闭/调整 IP 白名单后重试。"
            ) from e
        raise
    try:
        payload = {
            "common": {"app_id": app_id},
            "business": {
                "aue": "lame",
                "sfl": 1,
                "auf": "audio/L16;rate=16000",
                "vcn": vcn,
                "speed": speed,
                "volume": volume,
                "pitch": pitch,
                "tte": "UTF8",
            },
            "data": {
                "status": 2,
                "text": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
            },
        }
        ws.send(json.dumps(payload))

        chunks: list[bytes] = []
        while True:
            raw = ws.recv()
            if not raw:
                break
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            code = msg.get("code")
            if code is not None and code != 0:
                raise RuntimeError(
                    f"[article_tts] 讯飞错误 code={code} message={msg.get('message')}"
                )
            data = msg.get("data")
            if not data:
                continue
            audio_b64 = data.get("audio")
            if audio_b64:
                chunks.append(base64.b64decode(audio_b64))
            if data.get("status") == 2:
                break
        return b"".join(chunks)
    finally:
        ws.close()


def utf8_byte_chunks(text: str, max_bytes: int = 7800) -> list[str]:
    """按 UTF-8 字节上限切分（讯飞要求 base64 前 < 8000 字节）。"""
    text = text.strip()
    if not text:
        return []
    parts: list[str] = []
    buf: list[str] = []
    size = 0
    for para in text.split("\n"):
        line = para + "\n"
        b = line.encode("utf-8")
        if len(b) > max_bytes:
            if buf:
                parts.append("".join(buf).rstrip())
                buf = []
                size = 0
            for chunk in _hard_split(line, max_bytes):
                parts.append(chunk)
            continue
        if size + len(b) > max_bytes and buf:
            parts.append("".join(buf).rstrip())
            buf = []
            size = 0
        buf.append(line)
        size += len(b)
    if buf:
        parts.append("".join(buf).rstrip())
    return [p for p in parts if p.strip()]


def _hard_split(line: str, max_bytes: int) -> list[str]:
    out: list[str] = []
    cur = ""
    for ch in line:
        trial = cur + ch
        if len(trial.encode("utf-8")) > max_bytes and cur:
            out.append(cur)
            cur = ch
        else:
            cur = trial
    if cur.strip():
        out.append(cur)
    return out
