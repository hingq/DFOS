"""从 article.md 解析 **角色**:` 对话块并清洗文本。"""
from __future__ import annotations

import re

# briefing-article-style：**Q：** / **A：**（冒号在加粗内）；可选 **Qearl：**。
# 勿用 \w+（会把正文里 **加粗**： 误当成话轮）。
DIALOGUE_PATTERN = re.compile(
    r"\*\*(Q|A|Qearl)[:：]\*\*\s*(.+?)(?=\*\*(?:Q|A|Qearl)[:：]\*\*|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def parse_dialogues(md: str) -> list[tuple[str, str]]:
    """返回 (speaker_token, raw_segment) 列表。"""
    return DIALOGUE_PATTERN.findall(md)


def clean_segment_simple(text: str) -> str:
    """与旧 `generate_dialogue_audio` 的 clean_text 一致（段内去 markdown 噪声）。"""
    t = re.sub(r"#.*", "", text)
    t = re.sub(r"\*\*", "", t)
    t = re.sub(r"---", "", t)
    t = re.sub(r"##.*", "", t)
    t = re.sub(r"\n\n+", "\n", t)
    return t.strip()


def clean_segment_strip_role(text: str) -> str:
    """与旧 `clean_dialogue`（edge/noiz）一致：去掉段内可能的角色标记与版式。"""
    t = re.sub(r"\*\*(?:Q|A|Qearl)[:：]\*\*\s*", "", text, flags=re.IGNORECASE)
    t = re.sub(r"\*\*\w+\*\*[:：]\s*", "", t)
    t = re.sub(r"#.*", "", t)
    t = re.sub(r"---", "", t)
    t = re.sub(r"##.*", "", t)
    t = re.sub(r"\n\n+", "\n", t)
    return t.strip()
