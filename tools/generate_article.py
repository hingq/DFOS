"""日报对话式长文：从 processing 中按规则择 1 条，生成 {DATE}-article.md（口播母本）

选题：pipeline/article_pick.py  
体裁约束须与 .claude/skills/briefing-article-style/SKILL.md 一致（单产品、对话体、同表对齐）。
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import INTERMEDIATE_DIR, OUTPUT_DIR, load_context
from pipeline.article_pick import pick_primary_article_item_with_reason
from pipeline.llm import call_llm


def _default_date() -> str:
    return os.environ.get("BRIEFING_DATE") or datetime.now().strftime("%Y-%m-%d")


def load_processing_data(date: str) -> list:
    path = INTERMEDIATE_DIR / f"{date}-processing.json"
    if not path.exists():
        raise FileNotFoundError(f"找不到 processing 数据: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_article_dialogue(primary: dict, date: str) -> str:
    """单产品对话式全量分析（输出 Markdown，供 TTS）。"""
    style = load_context("style.md")[:4000]
    viewpoint = load_context("viewpoint.md")[:4000]
    expectations = load_context("expectations.md")[:6000]

    system = f"""你是「设计+AI日报」的深度稿件编辑，负责把**一条**资讯写成**对话式长文**（口播母本）。

## 固定角色（简化形式）
**Q**：主持人
**A**：嘉宾

## 写作要求
- 使用简化角色行：`Q：` + `A：`（不要用具体人名）
- 全文只围绕**这一条**资讯及其背后的产品/话题做「全量分析」，不要平均覆盖多条新闻
- 结构：标题 → 角色介绍 → 开场 → 2～4 个主题块（每块多轮对话、有观点碰撞）→ 编辑收束
- 事实以提供数据中的 key_facts、source 为准；推断需标明
- 可呼应「未来产品预期」维度（见下方 expectations 摘录），不必逐条点名
- 避免营销腔；关键概念可加粗
- 篇幅约 1500～4000 字

## 风格参考（摘录）
{style}

## 编辑视角参考（摘录）
{viewpoint}

## 未来产品预期参考（摘录，论述时可选用）
{expectations}
"""

    user = f"""日期：{date}

## 本条为当日选题（唯一主题）
{json.dumps(primary, ensure_ascii=False, indent=2)}

请输出完整 Markdown 正文，不要包在代码块里。"""
    return call_llm(system, user, max_tokens=8192)


def main():
    parser = argparse.ArgumentParser(description="生成对话式 article.md（单产品）")
    parser.add_argument(
        "--date",
        default=_default_date(),
        help="YYYY-MM-DD，默认今天或环境变量 BRIEFING_DATE",
    )
    args = parser.parse_args()
    date = args.date

    print(f"=== 对话式 article 生成: {date} ===")

    print("[article] 读取 processing …")
    processing_data = load_processing_data(date)
    print(f"  共 {len(processing_data)} 条")

    primary, reason = pick_primary_article_item_with_reason(processing_data)
    print(f"  {reason}")

    print("[article] 调用 LLM 生成对话稿 …")
    article = build_article_dialogue(primary, date)

    output_path = OUTPUT_DIR / f"{date}-article.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(article)

    print(f"✓ 已保存: {output_path}")
    print(f"  字符数: {len(article)}")


if __name__ == "__main__":
    main()
