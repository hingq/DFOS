"""信源清单配置

分三个优先级：
- P0: MVP 必须，第一天就接入
- P1: 第二阶段，跑通 1-2 周后接入
- P2: 按需扩展
"""

SOURCES = {
    # ============================================================
    # P0 — MVP 必须
    # ============================================================
    "p0": [
        {
            "name": "autocli",
            "type": "playwright",
            "url": "",  # 填入你的 Autocli URL
            "enabled": True,
            "selectors": {
                "card": ".item-card",       # 替换为实际选择器
                "title": ".title",
                "summary": ".summary",
                "link": "a",
            },
            "value": "一站式聚合，覆盖面广",
        },
        {
            "name": "product_hunt",
            "type": "rss",
            "url": "https://www.producthunt.com/feed",
            "enabled": True,
            "value": "每日新工具发现",
        },
        {
            "name": "the_rundown_ai",
            "type": "playwright",
            "url": "https://www.therundown.ai/",
            "enabled": False,  # P0 但需要单独写 scraper
            "value": "全球最大 AI newsletter",
        },
        {
            "name": "tldr_ai",
            "type": "playwright",
            "url": "https://tldr.tech/ai",
            "enabled": False,
            "value": "技术侧 AI 资讯",
        },
    ],

    # ============================================================
    # P1 — 设计 + UX
    # ============================================================
    "p1_design": [
        {"name": "ux_collective", "type": "rss", "url": "https://uxdesign.cc/feed",                    "enabled": True, "value": "最活跃设计社区"},
        {"name": "nng",           "type": "rss", "url": "https://www.nngroup.com/feed/rss/",            "enabled": False, "value": "UX 研究权威"},
        {"name": "smashing",      "type": "rss", "url": "https://www.smashingmagazine.com/feed/",       "enabled": True, "value": "前端+设计深度文章"},
        {"name": "prototypr",     "type": "rss", "url": "https://blog.prototypr.io/feed",               "enabled": False, "value": "原型设计与 UI 工具"},
        {"name": "dribbble",      "type": "rss", "url": "https://dribbble.com/stories.rss",             "enabled": False, "value": "设计师社区动态"},
        {"name": "designer_news", "type": "rss", "url": "https://www.designernews.co/stories/rss",       "enabled": True, "value": "Designer News"},
        {"name": "medium_design", "type": "rss", "url": "https://medium.design/feed",                  "enabled": True, "value": "Medium Design 专题"},
    ],

    # ============================================================
    # P2 — AI + 技术趋势
    # ============================================================
    "p2_ai": [
        {"name": "bens_bites",    "type": "rss", "url": "https://bensbites.beehiiv.com/feed",                          "enabled": False, "value": "AI 商业应用视角"},
        {"name": "import_ai",     "type": "rss", "url": "https://importai.substack.com/feed",                          "enabled": False, "value": "AI 研究与政策"},
        {"name": "the_verge_ai",  "type": "rss", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "enabled": False, "value": "科技大事件"},
        {"name": "techcrunch_ai", "type": "rss", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "enabled": False, "value": "融资收购速报"},
        {"name": "openai_blog",   "type": "rss", "url": "https://openai.com/blog/rss.xml",                             "enabled": False, "value": "OpenAI 一手信息"},
        {"name": "anthropic_blog","type": "rss", "url": "https://www.anthropic.com/blog/rss.xml",                       "enabled": False, "value": "Claude 更新与 AI 安全"},
        {"name": "google_ai",     "type": "rss", "url": "https://blog.google/technology/ai/rss/",                       "enabled": False, "value": "Google AI 动态"},
    ],

    # ============================================================
    # P2 — 产品管理
    # ============================================================
    "p2_product": [
        {"name": "product_talk",  "type": "rss", "url": "https://producttalk.org/feed",                "enabled": False, "value": "产品发现方法论"},
        {"name": "lennys",        "type": "rss", "url": "https://www.lennysnewsletter.com/feed",       "enabled": False, "value": "硅谷 PM 第一 newsletter"},
    ],

    # ============================================================
    # P2 — 中文信源
    # ============================================================
    "p2_chinese": [
        {"name": "sspai",         "type": "rss",        "url": "https://sspai.com/feed",       "enabled": False, "value": "中文效率工具"},
        {"name": "uisdc",         "type": "playwright",  "url": "https://www.uisdc.com/",      "enabled": False, "value": "中文设计师社区"},
        {"name": "ai_bot_cn",     "type": "playwright",  "url": "https://ai-bot.cn/",          "enabled": False, "value": "国内 AI 工具导航"},
    ],

    # ============================================================
    # P2 — 研究与前沿
    # ============================================================
    "p2_research": [
        {"name": "huggingface",   "type": "rss", "url": "https://huggingface.co/blog/feed.xml",        "enabled": False, "value": "开源 AI 模型动态"},
        {"name": "mit_tech",      "type": "rss", "url": "https://www.technologyreview.com/feed/",      "enabled": False, "value": "AI 社会影响"},
    ],

    # ============================================================
    # P3 — Twitter/X 博主（已启用）
    # ============================================================
    "p3_twitter": [
        {"name": "levelsio",     "type": "playwright", "url": "https://x.com/levelsio",                "enabled": True, "value": "AI 产品先驱，nomad list"},
        {"name": "swyx",         "type": "playwright", "url": "https://x.com/swyx",                    "enabled": True, "value": "AI 开发者布道者"},
        {"name": "jessica_chen", "type": "playwright", "url": "https://x.com/jessica",                 "enabled": True, "value": "AI 产品设计专家"},
        {"name": "steveschoger", "type": "playwright", "url": "https://x.com/steveschoger",             "enabled": True, "value": "UI 设计专家"},
        {"name": "mike_wallace", "type": "playwright", "url": "https://x.com/mike_wallace",             "enabled": True, "value": "AI UX 设计师"},
        {"name": "producthunt",  "type": "playwright", "url": "https://x.com/producthunt",             "enabled": True, "value": "每日产品发现"},
    ],

    # ============================================================
    # P2 — 行业工具博客
    # ============================================================
    "p2_tools": [
        {"name": "figma_blog",    "type": "rss", "url": "https://www.figma.com/blog/feed/",   "enabled": False, "value": "设计工具生态"},
        {"name": "vercel_blog",   "type": "rss", "url": "https://vercel.com/blog/rss.xml",    "enabled": False, "value": "前端与 AI 工程"},
    ],
}


def get_enabled_sources() -> list:
    """获取所有已启用的信源"""
    enabled = []
    for group_name, sources in SOURCES.items():
        for source in sources:
            if source.get("enabled", False):
                enabled.append(source)
    return enabled


def get_rss_sources() -> list:
    """获取已启用的 RSS 类型信源"""
    return [s for s in get_enabled_sources() if s["type"] == "rss"]


def get_playwright_sources() -> list:
    """获取已启用的 Playwright 类型信源"""
    return [s for s in get_enabled_sources() if s["type"] == "playwright"]