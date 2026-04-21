"""LLM 调用封装 — 支持 Anthropic 官方 / MiniMax 兼容"""
import json
import os
from anthropic import Anthropic, APIError

from config.settings import (
    LLM_MODEL,
    MINIMAX_ANTHROPIC_BASE_URL,
    MINIMAX_API_KEY,
    ANTHROPIC_API_KEY,
)


_client = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        # 优先用 Anthropic 官方，否则用 MiniMax
        api_key = ANTHROPIC_API_KEY or MINIMAX_API_KEY
        if not api_key.strip():
            raise ValueError("未配置 API KEY")

        # 判断用哪个端点
        if ANTHROPIC_API_KEY:
            base_url = None  # 官方
            model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        else:
            base_url = MINIMAX_ANTHROPIC_BASE_URL
            model = LLM_MODEL

        _client = Anthropic(
            api_key=api_key,
            base_url=base_url,
        )
        # 临时存 model
        _client._model = model
    return _client


def _message_text_from_response(response) -> str:
    """从 Anthropic 格式响应中提取全部文本块（忽略 thinking 等）。"""
    parts: list[str] = []
    for block in response.content:
        btype = getattr(block, "type", None)
        if btype == "text":
            t = getattr(block, "text", None)
            if t:
                parts.append(t)
        elif hasattr(block, "text") and not btype:
            parts.append(block.text)
    if parts:
        return "".join(parts)
    return str(response.content[0]) if response.content else ""


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """调用 LLM 并返回文本结果"""
    client = get_client()
    model = client._model  # 获取之前存的 model
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": user_prompt}],
            }
        ],
    )
    return _message_text_from_response(response)


def call_llm_json(system_prompt: str, user_prompt: str, max_retries: int = 3) -> list | dict:
    """调用 LLM 并解析 JSON 结果（仅对 JSON 解析失败重试；API 错误立即抛出）。"""
    import os
    import re

    raw = ""
    for attempt in range(max_retries):
        try:
            raw = call_llm(system_prompt, user_prompt)
        except APIError as e:
            print(f"  [llm] MiniMax/Anthropic 兼容 API 错误: {e}")
            raise

        try:
            # 清理 markdown 代码块，保留内部内容
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                if len(lines) > 1:
                    last_triple_backticks = cleaned.rfind("```")
                    if last_triple_backticks > 0:
                        start = len(lines[0]) + 1
                        cleaned = cleaned[start:last_triple_backticks].strip()
                    else:
                        cleaned = "\n".join(lines[1:]).strip()
            cleaned = cleaned.strip()

            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            cleaned = re.sub(r"'([^\']*)'", r'"\1"', cleaned)
            cleaned = re.sub(r"'(\w+)'", r'"\1"', cleaned)

            if os.getenv("DEBUG_LLM"):
                print("=== CLEANED JSON (before key/value fixes) ===")
                print(cleaned[:2000])

            cleaned = re.sub(r'(\w+):', r'"\1":', cleaned)
            cleaned = re.sub(r': (\w+)', r': "\1"', cleaned)
            cleaned = re.sub(r'(\d+)\.(\d+)', r'\1_DOT_\2', cleaned)
            # 修复 "4".8 → 4.8
            cleaned = re.sub(r'"(\d+)"\.(\d+)', r'\1.\2', cleaned)

            if os.getenv("DEBUG_LLM"):
                print("=== CLEANED JSON (final) ===")
                print(cleaned[:2000])

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️ JSON 解析失败，尝试 {attempt + 1}/{max_retries}")
                continue
            try:
                start = raw.find('[')
                if start >= 0:
                    depth = 0
                    in_string = False
                    escape = False
                    end = start
                    for i, c in enumerate(raw[start:], start):
                        if escape:
                            escape = False
                            continue
                        if c == '\\':
                            escape = True
                            continue
                        if c == '"':
                            in_string = not in_string
                            continue
                        if not in_string:
                            if c == '[' or c == '{':
                                depth += 1
                            elif c == ']' or c == '}':
                                depth -= 1
                                if depth == 0:
                                    end = i + 1
                                    break
                    if end > start:
                        cleaned = raw[start:end]
                        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
                        return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
            print(f"⚠️ JSON 解析最终失败: {e}")
            raise
