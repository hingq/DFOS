"""关键词白名单

分五个维度，与 context 文件的分类体系对齐。
权重：core(3x) > product/design(2x) > business(1.5x) > tech(1x)
"""

# AI × 设计（核心交叉领域 — 最高权重）
WHITELIST_CORE = [
    "AI design", "AI 设计", "AI prototyping", "AI UI", "AI UX",
    "design copilot", "设计副驾驶", "design assistant", "设计助手",
    "AI 生成界面", "AI-generated UI", "text to UI", "text to design",
    "AI layout", "AI 排版", "design automation", "设计自动化",
    "AI wireframe", "AI 线框图",
    # 工具名
    "Figma AI", "Framer AI", "Galileo AI", "Uizard",
    "Midjourney", "DALL-E", "Stable Diffusion", "Ideogram",
    "Adobe Firefly", "Canva AI", "Pika", "Runway",
    "Cursor", "v0", "bolt.new", "Lovable", "Replit Agent",
    # AI 交互模式
    "conversational UI", "对话式界面", "LUI", "language UI",
    "multimodal", "多模态", "voice UI", "语音交互",
    "AI agent", "AI 代理", "agentic", "智能体",
    "copilot", "副驾驶",
]

# 产品方法论
WHITELIST_PRODUCT = [
    "product discovery", "产品发现", "user research", "用户研究",
    "PMF", "product-market fit", "产品市场匹配",
    "MVP", "最小可行产品", "hypothesis", "假设验证",
    "A/B test", "A/B 测试", "retention", "留存",
    "churn", "流失", "onboarding", "用户引导",
    "activation", "激活", "product-led growth", "PLG",
    "产品驱动增长", "jobs to be done", "JTBD",
    "value proposition", "价值主张", "north star metric",
    "北极星指标", "product strategy", "产品战略",
    "first principles", "第一性原理",
]

# 体验设计
WHITELIST_DESIGN = [
    "design system", "设计系统", "design tokens",
    "component library", "组件库", "design language", "设计语言",
    "usability", "可用性", "accessibility", "无障碍", "a11y",
    "information architecture", "信息架构",
    "interaction design", "交互设计",
    "user flow", "用户流程", "user journey", "用户旅程",
    "cognitive load", "认知负担", "heuristic evaluation",
    "motion design", "动效设计", "micro-interaction", "微交互",
    "responsive", "响应式", "typography", "字体排版",
    "Figma", "Sketch", "Framer", "Webflow", "Spline",
]

# 商业与增长
WHITELIST_BUSINESS = [
    "SaaS", "subscription", "订阅", "freemium",
    "pricing", "定价", "monetization", "变现",
    "unit economics", "单位经济", "LTV", "CAC",
    "ARR", "MRR", "growth", "增长",
    "distribution", "分发", "SEO", "content marketing",
    "viral", "网络效应", "network effect",
    "funding", "融资", "acquisition", "收购",
    "YC", "Y Combinator", "a16z",
]

# 技术趋势
WHITELIST_TECH = [
    "GPT", "Claude", "Gemini", "Llama", "open source model",
    "fine-tuning", "微调", "RAG", "embedding",
    "reasoning", "推理", "chain of thought",
    "context window", "上下文窗口", "multimodal model",
    "API", "SDK", "MCP", "function calling", "tool use",
    "prompt engineering", "提示工程",
    "no-code", "低代码", "low-code", "AI-native", "AI 原生",
    "edge AI", "端侧 AI", "inference cost", "推理成本",
    "open source", "开源",
]

# 维度与权重映射
ALL_WHITELISTS = {
    "core": WHITELIST_CORE,
    "product": WHITELIST_PRODUCT,
    "design": WHITELIST_DESIGN,
    "business": WHITELIST_BUSINESS,
    "tech": WHITELIST_TECH,
}

KEYWORD_WEIGHTS = {
    "core": 3.0,
    "product": 2.0,
    "design": 2.0,
    "business": 1.5,
    "tech": 1.0,
}


def calculate_relevance(title: str, summary: str) -> float:
    """计算一条资讯的白名单相关性分数"""
    text = (title + " " + summary).lower()
    score = 0.0
    matched = []

    for category, keywords in ALL_WHITELISTS.items():
        weight = KEYWORD_WEIGHTS[category]
        for kw in keywords:
            if kw.lower() in text:
                score += weight
                matched.append((category, kw))

    return score, matched
