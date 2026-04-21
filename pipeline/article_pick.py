"""步骤 3 选题：从 processing 结果中选出「最值得单篇全量分析」的一条（通常为一个 AI 工具/产品）。

规则与 `.claude/skills/briefing-article-style/SKILL.md`、`context/expectations.md` 对齐，供 `tools/generate_article.py` 与 Agent 复用。
"""
from __future__ import annotations

# 简报层级：数值越小越优先
TIER_RANK = {
    "must_read": 0,
    "worth_noting": 1,
    "tool_radar": 2,
    "unknown": 5,
    "drop": 99,
}


def pick_primary_article_item(processing: list[dict]) -> dict:
    """
    从当日 processing 列表中选出 **一条** 作为 `article.md` 的主题。

    优先级（依次比较）：
    1. `category == "new_tool"` 优先（新工具/重大更新更适合产品向长文）
    2. `tier`：must_read > worth_noting > tool_radar
    3. `final_score` 降序

    Args:
        processing: `data/intermediate/{DATE}-processing.json` 解析后的列表

    Returns:
        单条 dict（含 one_liner、entities、tier、final_score 等）

    Raises:
        ValueError: processing 为空
    """
    if not processing:
        raise ValueError("processing 为空，无法选题")

    def sort_key(item: dict) -> tuple:
        cat = item.get("category") or ""
        new_tool_first = 0 if cat == "new_tool" else 1
        tier = item.get("tier") or "unknown"
        tr = TIER_RANK.get(tier, 5)
        fs = float(item.get("final_score") or 0.0)
        return (new_tool_first, tr, -fs)

    ranked = sorted(processing, key=sort_key)
    return ranked[0]


def pick_primary_article_item_with_reason(processing: list[dict]) -> tuple[dict, str]:
    """返回 (条目, 一句选题理由)。"""
    chosen = pick_primary_article_item(processing)
    cat = chosen.get("category", "")
    tier = chosen.get("tier", "")
    fs = chosen.get("final_score", "")
    products = (chosen.get("entities") or {}).get("products") or []
    name = products[0] if products else chosen.get("one_liner", "")[:40]
    reason = (
        f"选题: category={cat}, tier={tier}, final_score={fs}"
        + (f", 主产品「{name}」" if name else "")
    )
    return chosen, reason
