"""主流程 — 串联所有步骤

执行顺序：
1. 抓取（Playwright + RSS + 手动输入）
2. 预过滤（关键词黑白名单）
3. LLM 评分（6维加权）
4. LLM 分类（打标 + 实体提取）
5. LLM 生成简报（仅列表式 briefing.md）
6. 通知
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    RAW_DIR, INTERMEDIATE_DIR, OUTPUT_DIR,
    BRIEFING_MUST_READ, BRIEFING_WORTH_NOTING, BRIEFING_TOOL_RADAR,
    SCORING_POOL_SIZE, MIN_TWITTER_IN_SCORING_POOL, TWITTER_FINAL_SCORE_BONUS,
)
from scraper.base import load_all_raw
from scraper import autocli, rss, manual
from scraper import producthunt, hackernews
from pipeline.prefilter import prefilter
from pipeline.source_utils import is_twitter_item, select_pool_for_scoring
from pipeline.llm import call_llm, call_llm_json
from pipeline.prompts.scoring import SCORING_SYSTEM, SCORING_USER
from pipeline.prompts.processing import PROCESSING_SYSTEM, PROCESSING_USER
from pipeline.prompts.generation import build_generation_system, GENERATION_USER
from pipeline.deep_dive import (
    apply_processing_defaults,
    enrich_deep_dive_signals,
    pick_deep_dive_shortlist,
)
from pipeline.notify import notify


DATE = datetime.now().strftime("%Y-%m-%d")


def save_intermediate(step_name: str, data):
    """保存中间结果用于调试"""
    filepath = INTERMEDIATE_DIR / f"{DATE}-{step_name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved → {filepath.name}")


# ============================================================
# Step 0: 抓取
# ============================================================
def step_scrape() -> list[dict]:
    """执行所有已启用信源的抓取"""
    print("\n=== Step 0: Scrape ===")

    # P0 信源
    autocli.run()           # Autocli 聚合页（需要先配好选择器）
    rss.run()               # 所有已启用的 RSS 源
    manual.run()            # 手动输入

    # Playwright 独立 scraper
    producthunt.run()       # Product Hunt 首页
    hackernews.run()        # Hacker News

    raw_items = load_all_raw(RAW_DIR, DATE)
    print(f"  Total raw items: {len(raw_items)}")
    return raw_items


# ============================================================
# Step 1: 预过滤 + 评分
# ============================================================
def step_score(raw_items: list[dict]) -> tuple[list[dict], list[str]]:
    """预过滤 + LLM 评分，返回评分结果和对应的 source_url 列表"""
    print("\n=== Step 1: Prefilter + Score ===")

    # 预过滤
    filtered = prefilter(raw_items)

    # 选取进入评分的池子：略增大上限，并尽量纳入 Twitter 素材（见 config.settings）
    filtered = select_pool_for_scoring(
        filtered,
        max_size=SCORING_POOL_SIZE,
        min_twitter=MIN_TWITTER_IN_SCORING_POOL,
    )

    if not filtered:
        print("  No items passed prefilter")
        return [], []

    # 准备送入 LLM 的数据（去掉内部字段）
    items_for_llm = []
    source_urls = []  # 保存原始 source_url
    for i, item in enumerate(filtered):
        ch = "twitter" if is_twitter_item(item) else "other"
        items_for_llm.append({
            "index": i,
            "title": item.get("title", ""),
            "summary": item.get("summary", "")[:300],
            "source": item.get("source", ""),
            "source_url": item.get("source_url", ""),  # 保留给 LLM 参考
            "source_channel": ch,  # twitter | other，供评分与简报生成侧重
        })
        source_urls.append(item.get("source_url", ""))

    tw_in_pool = sum(1 for x in filtered if is_twitter_item(x))
    print(f"  Scoring pool: {len(items_for_llm)} items (twitter={tw_in_pool})")

    # LLM 评分
    print(f"  Sending {len(items_for_llm)} items to LLM for scoring...")
    scored = call_llm_json(
        SCORING_SYSTEM,
        SCORING_USER.format(
            count=len(items_for_llm),
            items_json=json.dumps(items_for_llm, ensure_ascii=False, indent=2),
        ),
    )

    save_intermediate("scoring", scored)

    # Twitter 渠道：在 LLM 打分后对 final_score 做小幅加成（同 tier 内更易进前排）
    for row in scored:
        idx = row.get("index", -1)
        if 0 <= idx < len(filtered) and is_twitter_item(filtered[idx]):
            fs = row.get("final_score")
            if isinstance(fs, (int, float)):
                row["final_score"] = round(
                    min(5.0, float(fs) + TWITTER_FINAL_SCORE_BONUS), 1
                )

    # 过滤掉 drop 层级
    passed = [item for item in scored if item.get("tier") != "drop"]

    # 按配额控制
    must_read = [i for i in passed if i["tier"] == "must_read"][:BRIEFING_MUST_READ]
    worth_noting = [i for i in passed if i["tier"] == "worth_noting"][:BRIEFING_WORTH_NOTING]
    tool_radar = [i for i in passed if i["tier"] == "tool_radar"][:BRIEFING_TOOL_RADAR]

    result = must_read + worth_noting + tool_radar

    # 恢复原始 source_url、source、source_channel（index 对应 filtered）
    for item in result:
        idx = item.get("index", 0)
        if idx < len(source_urls):
            item["source_url"] = source_urls[idx]
        if idx < len(filtered):
            item["source"] = filtered[idx].get("source", "")
            item["source_channel"] = "twitter" if is_twitter_item(filtered[idx]) else "other"

    print(f"  Scored: {len(must_read)} must_read, {len(worth_noting)} worth_noting, {len(tool_radar)} tool_radar")

    return result, source_urls


# ============================================================
# Step 2: 分类 + 实体提取
# ============================================================
def step_process(scored_items: list[dict], source_urls: list[str]) -> list[dict]:
    """深度处理：分类打标 + 实体提取"""
    print("\n=== Step 2: Process + Entity Extract ===")

    if not scored_items:
        print("  No items to process")
        return []

    print(f"  Processing {len(scored_items)} items...")
    processed = call_llm_json(
        PROCESSING_SYSTEM,
        PROCESSING_USER.format(
            count=len(scored_items),
            items_json=json.dumps(scored_items, ensure_ascii=False, indent=2),
        ),
    )

    # 合并评分和分类数据
    for i, item in enumerate(processed):
        if i < len(scored_items):
            s = scored_items[i]
            item["tier"] = s.get("tier", "worth_noting")
            item["final_score"] = s.get("final_score", 3.0)
            item["title"] = s.get("title", "")
            item["scoring_summary"] = s.get("summary", "")
            # 保留原始 source_url
            if i < len(source_urls):
                item["source_url"] = source_urls[i]
            for k in ("source", "source_channel"):
                if k in s:
                    item[k] = s[k]

    apply_processing_defaults(processed)
    save_intermediate("processing", processed)

    print(f"  Processed {len(processed)} items")
    return processed


# ============================================================
# Step 3: 生成简报
# ============================================================
def step_generate(
    processed_items: list[dict],
    deep_dive_shortlist: list[dict] | None = None,
) -> str:
    """生成最终简报 Markdown"""
    print("\n=== Step 3: Generate Briefing ===")

    if not processed_items:
        print("  No items to generate from")
        return ""

    system_prompt = build_generation_system()
    ddl = deep_dive_shortlist if deep_dive_shortlist is not None else []

    print(f"  Generating briefing from {len(processed_items)} items (深挖 {len(ddl)} 条)…")
    briefing = call_llm(
        system_prompt,
        GENERATION_USER.format(
            date=DATE,
            count=len(processed_items),
            deep_dive_shortlist_json=json.dumps(ddl, ensure_ascii=False, indent=2),
            items_json=json.dumps(processed_items, ensure_ascii=False, indent=2),
        ),
        max_tokens=8192,
    )

    # 保存
    filepath = OUTPUT_DIR / f"{DATE}-briefing.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(briefing)

    print(f"  Briefing saved → {filepath.name}")

    try:
        from tools.briefing_to_html import write_briefing_html

        html_path = write_briefing_html(filepath, DATE)
        print(f"  Briefing HTML → {html_path.relative_to(PROJECT_ROOT)}")
    except Exception as e:
        print(f"  [briefing] HTML 跳过: {e}")

    return briefing


# ============================================================
# 主流程
# ============================================================
def run(skip_scrape: bool = False):
    """执行完整 pipeline

    Args:
        skip_scrape: 跳过抓取步骤，直接使用 data/raw/ 中已有的数据。
                     用于测试 LLM 链路或手动抓取后单独跑处理。
    """
    print(f"\n{'='*60}")
    print(f"  Daily Briefing Pipeline — {DATE}")
    if skip_scrape:
        print(f"  (skip-scrape mode: using existing data)")
    print(f"{'='*60}")

    try:
        # Step 0: 抓取（可跳过）
        if skip_scrape:
            raw_items = load_all_raw(RAW_DIR, DATE)
            print(f"\n=== Step 0: Scrape (SKIPPED) ===")
            print(f"  Loaded {len(raw_items)} existing items from data/raw/")
        else:
            raw_items = step_scrape()

        if not raw_items:
            print("\n⚠️ No raw items. Check your sources or run: python -m tools.test_data")
            notify("")
            return

        # Step 1: 预过滤 + 评分
        scored_items, source_urls = step_score(raw_items)
        if not scored_items:
            print("\n⚠️ No items passed scoring.")
            notify("")
            return

        # Step 2: 分类 + 实体提取
        processed_items = step_process(scored_items, source_urls)

        # 深挖：raw 频次 enrich + 写回 intermediate（供 HTML/调试）
        enrich_deep_dive_signals(processed_items, RAW_DIR, DATE)
        save_intermediate("processing", processed_items)
        deep_dive_shortlist = pick_deep_dive_shortlist(processed_items)

        # Step 3: 生成列表式简报（对话式长文见 tools/generate_article.py → article.md）
        briefing = step_generate(processed_items, deep_dive_shortlist)

        # Step 4: 通知（推送到飞书/企业微信/OpenClaw）
        print("\n=== Step 4: Notify ===")
        notify(briefing)

        print(f"\n{'='*60}")
        print(f"  Done.")
        print(f"  简报: data/output/{DATE}-briefing.md")
        print(f"  简报网页: web/dist/briefing/{DATE}.html (Step 3 成功则已自动生成)")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        notify("")


if __name__ == "__main__":
    skip = "--skip-scrape" in sys.argv
    run(skip_scrape=skip)
