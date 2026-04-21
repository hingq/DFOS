"""预过滤：在调用 LLM 之前，用关键词做一轮快速筛选

方法二：信任信源仅过硬黑名单，不因关键词 0 分被挤出；与关键词路径合并后统一预算。
"""
from __future__ import annotations

from collections import defaultdict

from config.keywords import calculate_relevance
from config.blacklist import should_discard, calculate_penalty
from config.settings import MAX_LLM_INPUT, TWITTER_PREFILTER_BOOST
from config.trusted_sources import (
    TRUSTED_POOL_MAX,
    is_trusted_source,
    normalize_source_key,
    trusted_limit_for,
)
from pipeline.source_utils import is_twitter_item


def _dedupe_key(item: dict) -> str:
    """用于跨路径去重：优先 URL，无 URL 时用 source+title。"""
    u = (item.get("source_url") or "").strip().lower()
    if u:
        return u.split("#", 1)[0].split("?", 1)[0]
    src = item.get("source") or ""
    title = item.get("title") or ""
    return f"{src}|{title}"


def _annotate_keyword_item(item: dict) -> None:
    title = item.get("title", "")
    summary = item.get("summary", "")
    relevance, matched_keywords = calculate_relevance(title, summary)
    penalty = calculate_penalty(title, summary)
    final = relevance * penalty
    if is_twitter_item(item):
        final *= TWITTER_PREFILTER_BOOST
    item["_relevance"] = relevance
    item["_penalty"] = penalty
    item["_prefilter_score"] = final
    item["_matched_keywords"] = matched_keywords
    item["_prefilter_path"] = "keyword"


def _annotate_trusted_item(item: dict) -> None:
    """信任路径：仍计算关键词与软惩罚便于调试，但不靠分数决定是否准入。"""
    title = item.get("title", "")
    summary = item.get("summary", "")
    relevance, matched_keywords = calculate_relevance(title, summary)
    penalty = calculate_penalty(title, summary)
    final = relevance * penalty
    if is_twitter_item(item):
        final *= TWITTER_PREFILTER_BOOST
    item["_relevance"] = relevance
    item["_penalty"] = penalty
    item["_prefilter_score"] = final
    item["_matched_keywords"] = matched_keywords
    item["_prefilter_path"] = "trusted"


def _build_trusted_pool(trusted_items: list[dict]) -> tuple[list[dict], int]:
    """逐源配额 + 全局上限 + URL 去重；保持输入顺序稳定。"""
    per_source_used: dict[str, int] = defaultdict(int)
    seen_keys: set[str] = set()
    out: list[dict] = []
    skipped_dup = 0

    for item in trusted_items:
        if len(out) >= TRUSTED_POOL_MAX:
            break
        sk = normalize_source_key(item.get("source") or "")
        cap = trusted_limit_for(sk)
        if per_source_used[sk] >= cap:
            continue
        dk = _dedupe_key(item)
        if not dk or dk in seen_keys:
            if dk in seen_keys:
                skipped_dup += 1
            continue
        seen_keys.add(dk)
        _annotate_trusted_item(item)
        out.append(item)
        per_source_used[sk] += 1

    return out, skipped_dup


def _build_keyword_pool(normal_items: list[dict]) -> list[dict]:
    """非信任源：原关键词逻辑，产出至多 MAX_LLM_INPUT 条候选（合并前）。"""
    scored: list[dict] = []
    for item in normal_items:
        _annotate_keyword_item(item)
        scored.append(item)

    scored.sort(key=lambda x: x["_prefilter_score"], reverse=True)
    high_score = [i for i in scored if i["_prefilter_score"] > 0][:MAX_LLM_INPUT]
    if len(high_score) < 10:
        zero_score = [i for i in scored if i["_prefilter_score"] == 0]
        high_score.extend(zero_score[: 10 - len(high_score)])
    return high_score


def prefilter(raw_items: list[dict]) -> list[dict]:
    """
    预过滤流程：
    1. 硬黑名单 → 直接丢弃（信任 / 非信任均适用）
    2. 信任源：逐源 cap + TRUSTED_POOL_MAX + URL 去重 → 直通合并池
    3. 非信任源：白名单评分 + 软黑名单降权 → Top 候选
    4. 合并：信任条目优先（保证进入后续评分池的可达性），再补关键词路径；按 URL 去重；总长 ≤ MAX_LLM_INPUT
    """
    trusted_after_blacklist: list[dict] = []
    normal_after_blacklist: list[dict] = []
    discarded = 0

    for item in raw_items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        discard, _reason = should_discard(title, summary)
        if discard:
            discarded += 1
            continue
        src = item.get("source") or ""
        if is_trusted_source(src):
            trusted_after_blacklist.append(item)
        else:
            normal_after_blacklist.append(item)

    trusted_pool, trusted_inner_dup = _build_trusted_pool(trusted_after_blacklist)
    keyword_pool = _build_keyword_pool(normal_after_blacklist)

    seen = {_dedupe_key(x) for x in trusted_pool}
    merged: list[dict] = list(trusted_pool)
    kw_added = 0
    kw_skipped_dup = 0
    for item in keyword_pool:
        if len(merged) >= MAX_LLM_INPUT:
            break
        dk = _dedupe_key(item)
        if dk in seen:
            kw_skipped_dup += 1
            continue
        seen.add(dk)
        merged.append(item)
        kw_added += 1

    tw = sum(1 for x in merged if x.get("_prefilter_path") == "trusted")
    kw = sum(1 for x in merged if x.get("_prefilter_path") == "keyword")
    print(
        f"  Prefilter: {len(raw_items)} raw → {discarded} blacklisted → "
        f"merged={len(merged)} (trusted={tw}, keyword={kw}; "
        f"trusted_dup_skip={trusted_inner_dup}, kw_dup_skip={kw_skipped_dup}) → LLM pool"
    )
    return merged
