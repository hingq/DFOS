"""生成测试数据

用来在不配置真实信源的情况下跑通 LLM pipeline。
运行: python -m tools.test_data
"""
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import RAW_DIR

TEST_ITEMS = [
    {
        "source": "twitter / X",
        "title": "[社区热议] 某 AI 设计工具在 X 上被大量转发讨论工作流替代",
        "summary": "一线设计师在 Twitter/X 上讨论该工具是否改变交付方式；话题在当日时间线中热度较高，适合验证 pipeline 对 Twitter 素材与权重的处理。",
        "source_url": "https://twitter.com/example/status/0000000000",
        "author": "@design_ops_example",
        "published_at": datetime.now().isoformat(),
        "tags": ["twitter", "AI", "workflow"],
    },
    {
        "source": "test",
        "title": "Figma 发布 AI 自动布局功能，可根据内容描述生成完整页面",
        "summary": "Figma 在今天的发布会上推出了 AI Auto Layout 功能，设计师只需用自然语言描述页面需求，系统即可自动生成符合设计规范的响应式布局。该功能支持与现有 Design System 集成。",
        "source_url": "https://example.com/figma-ai-layout",
        "author": "Figma Team",
        "published_at": datetime.now().isoformat(),
        "tags": ["AI", "design", "Figma"],
    },
    {
        "source": "test",
        "title": "Cursor 推出多文件编辑模式，支持跨项目上下文理解",
        "summary": "AI 代码编辑器 Cursor 发布 v0.45，新增 Multi-File Edit 功能，可以同时理解和修改多个关联文件。团队表示这是向 AI Agent 编程迈出的关键一步。",
        "source_url": "https://example.com/cursor-multi-file",
        "author": "Cursor Blog",
        "published_at": datetime.now().isoformat(),
        "tags": ["AI", "coding", "Cursor"],
    },
    {
        "source": "test",
        "title": "Anthropic 将 Claude 的上下文窗口扩展至 1M tokens",
        "summary": "Anthropic 宣布 Claude 模型系列支持 100 万 token 上下文窗口，适用于长文档分析、代码库理解等场景。定价与现有模型保持一致。",
        "source_url": "https://example.com/claude-1m-context",
        "author": "Anthropic",
        "published_at": datetime.now().isoformat(),
        "tags": ["AI", "LLM", "Anthropic"],
    },
    {
        "source": "test",
        "title": "设计工具 Framer 被 Canva 以 8 亿美元收购",
        "summary": "Canva 宣布收购网页设计工具 Framer，交易价格约 8 亿美元。Canva 表示将保留 Framer 的独立品牌和团队，但会整合其 AI 生成网页的能力。",
        "source_url": "https://example.com/canva-framer-acquisition",
        "author": "TechCrunch",
        "published_at": datetime.now().isoformat(),
        "tags": ["acquisition", "design", "business"],
    },
    {
        "source": "test",
        "title": "Nielsen Norman Group 发布 AI 界面可用性研究报告",
        "summary": "NNg 最新研究显示，78% 的用户在使用 AI 聊天界面时会遇到 3 个以上的可用性问题。报告建议采用渐进式披露和结果可视化来改善 AI 产品体验。",
        "source_url": "https://example.com/nng-ai-usability",
        "author": "NNg Research",
        "published_at": datetime.now().isoformat(),
        "tags": ["UX", "research", "AI"],
    },
    {
        "source": "test",
        "title": "开源设计工具 Penpot 集成 AI 图层命名和组件建议",
        "summary": "Penpot 在最新版本中加入 AI 辅助功能，可自动为图层命名、建议组件复用、检测设计一致性问题。该功能完全开源，可私有化部署。",
        "source_url": "https://example.com/penpot-ai",
        "author": "Penpot Blog",
        "published_at": datetime.now().isoformat(),
        "tags": ["design", "open source", "AI"],
    },
    {
        "source": "test",
        "title": "Product Hunt 本周最热：AI 简历优化工具获得 1200+ upvotes",
        "summary": "一款名为 ResumeAI 的工具本周在 Product Hunt 获得大量关注，可根据职位描述自动优化简历内容和排版。创始人表示是独立开发者，用 3 周时间完成。",
        "source_url": "https://example.com/resumeai-ph",
        "author": "Product Hunt",
        "published_at": datetime.now().isoformat(),
        "tags": ["tool", "AI", "productivity"],
    },
    {
        "source": "test",
        "title": "为什么大多数 AI 产品的留存率不到 10%",
        "summary": "一篇来自 a16z 合伙人的分析文章，指出当前 AI 产品面临严重的留存问题。核心观点：大多数 AI wrapper 没有形成用户习惯，需要从工作流整合而非功能创新角度思考。",
        "source_url": "https://example.com/ai-retention-problem",
        "author": "a16z",
        "published_at": datetime.now().isoformat(),
        "tags": ["AI", "product", "growth"],
    },
    {
        "source": "test",
        "title": "Vercel 发布 v0 企业版，支持团队协作和品牌设计系统",
        "summary": "v0 by Vercel 推出企业版本，新增团队共享 prompt 库、品牌 design token 导入、私有组件库对接等功能。定价 $49/seat/month。",
        "source_url": "https://example.com/v0-enterprise",
        "author": "Vercel Blog",
        "published_at": datetime.now().isoformat(),
        "tags": ["AI", "design", "tool", "enterprise"],
    },
    {
        "source": "test",
        "title": "10 个你不能错过的免费 AI 设计工具",
        "summary": "整理了 2026 年最值得使用的免费 AI 设计工具，包括图片生成、排版辅助、配色建议等多个类别。每个工具附有简短评测和适用场景说明。",
        "source_url": "https://example.com/10-free-ai-tools",
        "author": "设计博客",
        "published_at": datetime.now().isoformat(),
        "tags": ["AI", "tools", "list"],
    },
]


def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = RAW_DIR / f"{date_str}-test.json"

    for item in TEST_ITEMS:
        item["scraped_at"] = datetime.now().isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(TEST_ITEMS, f, ensure_ascii=False, indent=2)

    print(f"✓ Generated {len(TEST_ITEMS)} test items → {filepath}")
    print(f"  Now run: python -m pipeline.main --skip-scrape")


if __name__ == "__main__":
    main()
