"""完成通知 — 推送到飞书/企业微信/Bark/OpenClaw

推送内容基于列表式简报（briefing.md）。对话式长文与口播以 `data/output/*-article.md` 为准，不再生成 briefing-chat.md。
"""
import os
import requests
from datetime import datetime
from config.settings import FEISHU_WEBHOOK, WECHAT_WEBHOOK, BARK_TOKEN

# OpenClaw 配置
OPENCLAW_API_URL = os.getenv("OPENCLAW_API_URL", "")
OPENCLAW_API_KEY = os.getenv("OPENCLAW_API_KEY", "")
OPENCLAW_CHANNEL = os.getenv("OPENCLAW_CHANNEL", "daily-briefing")


def notify(briefing: str):
    """发送通知

    Args:
        briefing: 列表式简报内容（来自 briefing.md 生成结果）
    """
    date = datetime.now().strftime("%Y-%m-%d")
    sent = False

    if not briefing:
        msg = f"⚠️ {date} 日报生成失败，请检查日志。"
        if FEISHU_WEBHOOK:
            _notify_feishu(msg, "")
        if WECHAT_WEBHOOK:
            _notify_wechat(msg, "")
        return

    preview = briefing[:300].replace("\n", " ")
    title = f"📰 {date} 日报草稿已生成"

    # 飞书/企业微信/Bark → 推送简短通知
    if FEISHU_WEBHOOK:
        sent = _notify_feishu(title, f"{preview}...\n\n请审核后发布。") or sent
    if WECHAT_WEBHOOK:
        sent = _notify_wechat(title, f"{preview}...\n\n请审核后发布。") or sent
    if BARK_TOKEN:
        sent = _notify_bark(title, preview) or sent

    # OpenClaw → 推送列表式简报正文
    if OPENCLAW_API_URL:
        sent = _notify_openclaw(date, briefing) or sent

    if not sent:
        print(f"  [notify] No channel configured. Files ready:")
        print(f"    简报: data/output/{date}-briefing.md")


def _notify_openclaw(date: str, content: str) -> bool:
    """推送到 OpenClaw

    接口格式根据你的 OpenClaw 服务器调整。
    当前假设: POST /api/messages，JSON body。
    """
    try:
        payload = {
            "channel": OPENCLAW_CHANNEL,
            "title": f"设计+AI日报 {date}",
            "content": content,
            "date": date,
            "type": "daily_briefing",
        }
        headers = {"Content-Type": "application/json"}
        if OPENCLAW_API_KEY:
            headers["Authorization"] = f"Bearer {OPENCLAW_API_KEY}"

        resp = requests.post(
            f"{OPENCLAW_API_URL}/api/messages",
            json=payload,
            headers=headers,
            timeout=15,
        )
        if resp.status_code in (200, 201):
            print(f"  [notify:openclaw] Sent ({resp.status_code})")
            return True
        else:
            print(f"  [notify:openclaw] Failed ({resp.status_code}): {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  [notify:openclaw] Error: {e}")
        return False


def _notify_feishu(title: str, body: str) -> bool:
    try:
        resp = requests.post(FEISHU_WEBHOOK, json={
            "msg_type": "text",
            "content": {"text": f"{title}\n\n{body}"}
        }, timeout=10)
        print(f"  [notify:feishu] Sent ({resp.status_code})")
        return resp.status_code == 200
    except Exception as e:
        print(f"  [notify:feishu] Error: {e}")
        return False


def _notify_wechat(title: str, body: str) -> bool:
    try:
        resp = requests.post(WECHAT_WEBHOOK, json={
            "msgtype": "text",
            "text": {"content": f"{title}\n\n{body}"}
        }, timeout=10)
        print(f"  [notify:wechat] Sent ({resp.status_code})")
        return resp.status_code == 200
    except Exception as e:
        print(f"  [notify:wechat] Error: {e}")
        return False


def _notify_bark(title: str, body: str) -> bool:
    try:
        resp = requests.get(
            f"https://api.day.app/{BARK_TOKEN}/{title}/{body[:200]}",
            timeout=10,
        )
        print(f"  [notify:bark] Sent ({resp.status_code})")
        return resp.status_code == 200
    except Exception as e:
        print(f"  [notify:bark] Error: {e}")
        return False
