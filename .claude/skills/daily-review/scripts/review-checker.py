"""日报审核辅助脚本

自动执行审核 checklist 中的可量化检查项：
1. 头条排序是否正确（最高分在第一位）
2. 评分分布是否合理
3. 分类覆盖度
4. 实体提取统计
5. 与历史数据对比

用法（在项目根目录执行）: python .claude/skills/daily-review/scripts/review-checker.py [日期]
默认检查今天的数据。
"""
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# scripts → daily-review → skills → .claude → 项目根
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_json(filepath: Path) -> list | dict | None:
    if not filepath.exists():
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def check_briefing_exists(date: str) -> dict:
    """检查简报文件是否存在"""
    briefing_path = DATA_DIR / "output" / f"{date}-briefing.md"
    scoring_path = DATA_DIR / "intermediate" / f"{date}-scoring.json"
    processing_path = DATA_DIR / "intermediate" / f"{date}-processing.json"

    return {
        "briefing": briefing_path.exists(),
        "scoring": scoring_path.exists(),
        "processing": processing_path.exists(),
        "briefing_path": str(briefing_path),
        "scoring_path": str(scoring_path),
        "processing_path": str(processing_path),
    }


def check_headline(scoring: list) -> dict:
    """检查头条：最高分条目是否在第一位"""
    if not scoring:
        return {"status": "skip", "reason": "no scoring data"}

    # 找出非 drop 的条目
    kept = [s for s in scoring if s.get("tier") != "drop"]
    if not kept:
        return {"status": "skip", "reason": "no items passed scoring"}

    # 按 final_score 排序
    sorted_by_score = sorted(kept, key=lambda x: x.get("final_score", 0), reverse=True)
    top_item = sorted_by_score[0]
    first_item = kept[0]

    if top_item.get("title") == first_item.get("title"):
        return {
            "status": "pass",
            "top_title": top_item.get("title", "")[:60],
            "top_score": top_item.get("final_score", 0),
        }
    else:
        return {
            "status": "warn",
            "message": "Headline mismatch",
            "current_first": first_item.get("title", "")[:60],
            "should_be_first": top_item.get("title", "")[:60],
            "current_score": first_item.get("final_score", 0),
            "top_score": top_item.get("final_score", 0),
        }


def check_score_distribution(scoring: list) -> dict:
    """检查评分分布"""
    if not scoring:
        return {"status": "skip"}

    tiers = {"must_read": 0, "worth_noting": 0, "tool_radar": 0, "drop": 0}
    scores = []

    for item in scoring:
        tier = item.get("tier", "drop")
        tiers[tier] = tiers.get(tier, 0) + 1
        scores.append(item.get("final_score", 0))

    avg_score = sum(scores) / len(scores) if scores else 0
    kept = len(scoring) - tiers.get("drop", 0)

    warnings = []
    if tiers.get("must_read", 0) > 4:
        warnings.append(f"must_read too many ({tiers['must_read']}), expected ≤3")
    if tiers.get("must_read", 0) == 0 and kept > 0:
        warnings.append("no must_read items — is today really that quiet?")
    if kept > 15:
        warnings.append(f"too many items kept ({kept}), briefing may be too long")
    if kept < 3:
        warnings.append(f"only {kept} items — consider lowering thresholds or adding sources")

    return {
        "status": "warn" if warnings else "pass",
        "tiers": tiers,
        "total": len(scoring),
        "kept": kept,
        "avg_score": round(avg_score, 2),
        "warnings": warnings,
    }


def check_entities(processing: list) -> dict:
    """统计实体提取结果"""
    if not processing:
        return {"status": "skip"}

    all_products = []
    all_companies = []

    for item in processing:
        entities = item.get("entities", {})
        all_products.extend(entities.get("products", []))
        all_companies.extend(entities.get("companies", []))

    # 去重统计
    product_counts = {}
    for p in all_products:
        product_counts[p] = product_counts.get(p, 0) + 1

    company_counts = {}
    for c in all_companies:
        company_counts[c] = company_counts.get(c, 0) + 1

    return {
        "status": "pass",
        "unique_products": len(product_counts),
        "unique_companies": len(company_counts),
        "top_products": sorted(product_counts.items(), key=lambda x: -x[1])[:5],
        "top_companies": sorted(company_counts.items(), key=lambda x: -x[1])[:5],
    }


def check_category_coverage(processing: list) -> dict:
    """检查分类覆盖度"""
    if not processing:
        return {"status": "skip"}

    categories = {}
    for item in processing:
        cat = item.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    expected = {"new_tool", "case_study", "trend", "methodology", "opinion"}
    covered = set(categories.keys()) & expected
    missing = expected - covered

    return {
        "status": "pass" if len(missing) <= 2 else "info",
        "categories": categories,
        "missing": list(missing) if missing else [],
        "message": f"Covered {len(covered)}/5 categories" + (f", missing: {', '.join(missing)}" if missing else ""),
    }


def check_briefing_length(date: str) -> dict:
    """检查简报长度"""
    filepath = DATA_DIR / "output" / f"{date}-briefing.md"
    if not filepath.exists():
        return {"status": "skip"}

    content = filepath.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    chars = len(content)
    sections = [l for l in lines if l.startswith("### ") or l.startswith("## ")]

    warnings = []
    if chars > 5000:
        warnings.append(f"Briefing is long ({chars} chars), reader may not finish")
    if chars < 500:
        warnings.append(f"Briefing is very short ({chars} chars)")

    return {
        "status": "warn" if warnings else "pass",
        "lines": len(lines),
        "chars": chars,
        "sections": len(sections),
        "warnings": warnings,
    }


def run_review(date: str = None):
    """执行完整审核检查"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'='*55}")
    print(f"  Daily Review Checker — {date}")
    print(f"{'='*55}\n")

    # 0. 文件检查
    files = check_briefing_exists(date)
    if not files["briefing"]:
        print(f"❌ Briefing not found: {files['briefing_path']}")
        print(f"   Run: python -m pipeline.main")
        return

    # 加载数据
    scoring = load_json(Path(files["scoring_path"])) or []
    processing = load_json(Path(files["processing_path"])) or []

    results = {}

    # 1. 头条检查
    results["headline"] = check_headline(scoring)
    status = results["headline"]["status"]
    if status == "pass":
        title = results["headline"].get("top_title", "")
        score = results["headline"].get("top_score", 0)
        print(f"✅ Headline: {title} (score: {score})")
    elif status == "warn":
        print(f"⚠️  Headline mismatch!")
        print(f"   Current:  {results['headline'].get('current_first', '')} ({results['headline'].get('current_score', 0)})")
        print(f"   Should be: {results['headline'].get('should_be_first', '')} ({results['headline'].get('top_score', 0)})")

    # 2. 评分分布
    results["distribution"] = check_score_distribution(scoring)
    dist = results["distribution"]
    if dist["status"] != "skip":
        tiers = dist.get("tiers", {})
        print(f"\n📊 Score distribution: {dist['kept']} kept / {dist['total']} total (avg: {dist['avg_score']})")
        print(f"   must_read: {tiers.get('must_read', 0)} | worth_noting: {tiers.get('worth_noting', 0)} | tool_radar: {tiers.get('tool_radar', 0)} | drop: {tiers.get('drop', 0)}")
        for w in dist.get("warnings", []):
            print(f"   ⚠️  {w}")

    # 3. 分类覆盖
    results["categories"] = check_category_coverage(processing)
    cat = results["categories"]
    if cat["status"] != "skip":
        print(f"\n📂 Categories: {cat['message']}")

    # 4. 实体统计
    results["entities"] = check_entities(processing)
    ent = results["entities"]
    if ent["status"] != "skip":
        print(f"\n🏷️  Entities: {ent['unique_products']} products, {ent['unique_companies']} companies")
        if ent.get("top_products"):
            top = ", ".join(f"{p[0]}({p[1]})" for p in ent["top_products"][:3])
            print(f"   Top products: {top}")

    # 5. 简报长度
    results["length"] = check_briefing_length(date)
    length = results["length"]
    if length["status"] != "skip":
        print(f"\n📏 Length: {length['lines']} lines, {length['chars']} chars, {length['sections']} sections")
        for w in length.get("warnings", []):
            print(f"   ⚠️  {w}")

    # 总结
    all_warnings = []
    for key, val in results.items():
        if val.get("status") == "warn":
            all_warnings.extend(val.get("warnings", []))
            if val.get("message"):
                all_warnings.append(val["message"])

    print(f"\n{'='*55}")
    if all_warnings:
        print(f"  ⚠️  {len(all_warnings)} warnings — review before publishing")
    else:
        print(f"  ✅ All checks passed — ready to publish")
    print(f"{'='*55}")
    print(f"\n  Briefing: {files['briefing_path']}")
    print(f"  Next: review the briefing, then publish\n")

    # 输出 JSON 结果（供 Claude Code 读取）
    return results


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_review(date_arg)
