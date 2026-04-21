# 科大讯飞流式语音合成（WebSocket v2）

## 官方文档

- 接口说明：<https://www.xfyun.cn/doc/tts/online_tts/API.html>
- 产品页：<https://www.xfyun.cn/services/online_tts>

## 本仓库实现

- 模块：`tools/article_tts/xfyun_ws.py`
- 入口：`python -m tools.article_tts`
- 协议：`wss://tts-api.xfyun.cn/v2/tts`，鉴权为 `hmac-sha256`（`host` + `date` + `request-line`）
- 音频：`aue=lame`、`sfl=1`、16k MP3 流式拼接

## 依赖

- `websocket-client`（见项目 `requirements.txt`）
- 系统 `ffmpeg`（合并分段 MP3，与 `tools/tts_dialogue` 相同）

## 试用与额度

以讯飞控制台与文档为准；常见为每日有限次免费试用，超出需购买或领包。

## 常见错误

| 现象 | 处理 |
|------|------|
| `401` / 签名失败 | 核对 `API_KEY`、`API_SECRET` 是否复制完整、系统时间是否准确 |
| `11200` | 发音人未授权或额度不足 |
| `10109` / 文本过长 | 单段已按 UTF-8 字节自动切分；仍报错可缩短单段正文 |
