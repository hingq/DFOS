"""值得深挖：原始素材频次 enrich + 短名单选取（0～2 条）。

深挖列表 100% 对应当日 processing 条目；合并同一 anchor_product 的多条能力。
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import DEEP_DIVE_SIGNAL_DAYS

# 仅当 release_evidence 属于官宣类时，strong 才可进短名单
OFFICIAL_RELEASE_EVIDENCE = frozenset(
    {
        "official_changelog",
        "official_blog",
        "press_release",
        "app_release_notes",
    }
)


def _item_text_blob(item: dict) -> str:
    t = (item.get("title") or "") + " " + (item.get("summary") or "")
    return t.lower()


def _normalize_key(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip().lower())


def load_raw_for_date(raw_dir: Path, date_str: str) -> list[dict]:
    items: list[dict] = []
    for filepath in sorted(raw_dir.glob(f"{date_str}-*.json")):
        with open(filepath, encoding="utf-8") as f:
            items.extend(json.load(f))
    return items


def load_raw_last_ndays(raw_dir: Path, end_date_str: str, ndays: int) -> list[dict]:
    """合并最近 ndays 天（含 end 当日）所有 raw 条目。"""
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    out: list[dict] = []
    for i in range(max(1, ndays)):
        d = (end_dt - timedelta(days=i)).strftime("%Y-%m-%d")
        out.extend(load_raw_for_date(raw_dir, d))
    return out


def count_product_mentions(anchor_product: str, raw_items: list[dict]) -> int:
    """统计原始条目中标题+摘要是否包含产品名（不强制 capability，避免漏计）。"""
    key = _normalize_key(anchor_product)
    if not key:
        return 0
    n = 0
    for it in raw_items:
        blob = _item_text_blob(it)
        if key in blob:
            n += 1
    return n


def enrich_deep_dive_signals(
    processed: list[dict],
    raw_dir: Path,
    date_str: str,
    ndays: int | None = None,
) -> None:
    """就地写入 signal_same_day_count、signal_ndays_count。"""
    ndays = ndays if ndays is not None else DEEP_DIVE_SIGNAL_DAYS
    today_raw = load_raw_for_date(raw_dir, date_str)
    ranged_raw = load_raw_last_ndays(raw_dir, date_str, ndays)

    for row in processed:
        ap = (row.get("anchor_product") or "").strip()
        if not ap:
            row["signal_same_day_count"] = 0
            row["signal_ndays_count"] = 0
            continue
        row["signal_same_day_count"] = count_product_mentions(ap, today_raw)
        row["signal_ndays_count"] = count_product_mentions(ap, ranged_raw)


def _display_name(anchor_product: str, capabilities: list[str]) -> str:
    caps = [c.strip() for c in capabilities if c and str(c).strip()]
    caps = list(dict.fromkeys(caps))
    if caps:
        cap_str = "、".join(caps)
        return f"{anchor_product.strip()} · {cap_str}"
    return anchor_product.strip()


def _ensure_processing_defaults(row: dict) -> None:
    row.setdefault("release_kind", "not_product")
    row.setdefault("anchor_product", "")
    row.setdefault("anchor_capability", "")
    row.setdefault("ai_involvement", "none")
    row.setdefault("deep_dive_fit", "none")
    row.setdefault("release_evidence", "unknown")


def apply_processing_defaults(processed: list[dict]) -> None:
    """补齐 LLM 未返回的旧字段，避免 enrich/筛选 KeyError。"""
    for row in processed:
        _ensure_processing_defaults(row)


def _eligible_for_shortlist(row: dict) -> bool:
    _ensure_processing_defaults(row)
    if row.get("deep_dive_fit") != "strong":
        return False
    if row.get("release_kind") not in ("standalone_tool", "host_feature"):
        return False
    if row.get("ai_involvement") != "core":
        return False
    ev = row.get("release_evidence") or "unknown"
    if ev not in OFFICIAL_RELEASE_EVIDENCE:
        return False
    if not (row.get("anchor_product") or "").strip():
        return False
    return True


def _group_key(row: dict) -> str:
    return _normalize_key(row.get("anchor_product") or "")


def pick_deep_dive_shortlist(processed: list[dict], max_items: int = 2) -> list[dict]:
    """从 processing 中选出 0～max_items 条展示用短名单（已按宿主合并）。"""
    for row in processed:
        _ensure_processing_defaults(row)

    eligible_idxs = [i for i, p in enumerate(processed) if _eligible_for_shortlist(p)]
    if not eligible_idxs:
        return []

    buckets: dict[str, list[int]] = {}
    for i in eligible_idxs:
        row = processed[i]
        k = _group_key(row)
        if not k:
            continue
        buckets.setdefault(k, []).append(i)

    merged: list[dict] = []
    for _k, idxs in buckets.items():
        rows = [processed[i] for i in idxs]
        rows.sort(
            key=lambda r: (
                -float(r.get("final_score") or 0),
                -int(r.get("signal_same_day_count") or 0),
                -int(r.get("signal_ndays_count") or 0),
            )
        )
        best = rows[0]
        caps: list[str] = []
        for r in rows:
            c = (r.get("anchor_capability") or "").strip()
            if c and c not in caps:
                caps.append(c)
        ap = (best.get("anchor_product") or "").strip()
        std = _display_name(ap, caps)
        merged.append(
            {
                "standard_display_name": std,
                "anchor_product": ap,
                "anchor_capabilities": caps,
                "release_kind": best.get("release_kind"),
                "one_liner": best.get("one_liner", ""),
                "key_facts": best.get("key_facts", ""),
                "impact": best.get("impact", ""),
                "source_url": best.get("source_url", ""),
                "source_name": best.get("source_name") or best.get("source", ""),
                "tier": best.get("tier", ""),
                "final_score": best.get("final_score", 0),
                "signal_same_day_count": max(int(r.get("signal_same_day_count") or 0) for r in rows),
                "signal_ndays_count": max(int(r.get("signal_ndays_count") or 0) for r in rows),
                "processing_indices": [processed[j].get("index") for j in idxs],
            }
        )

    type_rank = {"standalone_tool": 0, "host_feature": 1, "not_product": 9}

    def sort_m(m: dict) -> tuple:
        rk = m.get("release_kind") or "not_product"
        return (
            -int(m.get("signal_same_day_count") or 0),
            -int(m.get("signal_ndays_count") or 0),
            -float(m.get("final_score") or 0),
            type_rank.get(rk, 9),
        )

    merged.sort(key=sort_m)
    return merged[:max_items]
