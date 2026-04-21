"""信源识别与评分池选取 — Twitter 等对简报权重的可配置影响"""

from __future__ import annotations


def is_twitter_item(item: dict) -> bool:
    """判断一条 raw 是否来自 Twitter/X（用于预过滤加权与评分池保障）。"""
    src = (item.get("source") or "").lower()
    if "twitter" in src or "x.com" in src or src in ("x", "twitter/x"):
        return True
    tags = item.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    for t in tags:
        if "twitter" in str(t).lower() or str(t).lower() in ("x", "tweet"):
            return True
    url = (item.get("source_url") or "").lower()
    if "twitter.com" in url or "x.com/" in url:
        return True
    return False


def select_pool_for_scoring(
    filtered: list[dict],
    max_size: int,
    min_twitter: int,
) -> list[dict]:
    """
    在预过滤排序结果上截取进入 LLM 评分的池子。
    尽量保证池中包含至多 min_twitter 条 Twitter 条目（若存在），其余按原排序补齐。
    """
    if max_size <= 0:
        return []
    if len(filtered) <= max_size:
        return filtered

    tw = [x for x in filtered if is_twitter_item(x)]
    take_tw = tw[: min(min_twitter, len(tw))]
    taken_ids = {id(x) for x in take_tw}
    rest = [x for x in filtered if id(x) not in taken_ids]
    out = take_tw + rest[: max_size - len(take_tw)]
    return out[:max_size]
