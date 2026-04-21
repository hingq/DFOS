"""关键词白名单 — 精准狙击版

设计原则（参考"坏关键词 vs 好关键词"）:
- 坏: "AI" → 什么都命中，等于没过滤
- 好: "Claude Code agent loop" → 精准命中特定话题

每个关键词应该满足:
1. 命中它的文章，80%+ 概率是你读者想看的
2. 不命中它的文章，不代表不值得看（那是 LLM 评分的事）
3. 足够具体，不会误命中无关内容

三层结构:
- exact: 精确匹配的工具名/专有名词（短且唯一）
- phrase: 2-4 词组合短语（描述特定话题）
- combo: 需要同时出现两个词才算命中（降低误命中）
"""

# ============================================================
# 第一层: 精确匹配 — 工具名/产品名/专有名词
# 命中即相关，不需要上下文
# ============================================================

EXACT_CORE = [
    # AI 设计工具（命中 = 一定跟设计师有关）
    "Figma AI", "Framer AI", "Galileo AI", "Uizard",
    "Adobe Firefly", "Canva Magic", "Penpot AI",
    "Spline AI", "Motiff", "Locofy",
    # AI 编码/生成工具（PM/设计师直接用的）
    "Cursor", "Windsurf", "v0.dev", "bolt.new",
    "Lovable", "Replit Agent", "Claude Code",
    "GitHub Copilot Workspace", "Devin",
    # AI 图像/视频（设计师工作流）
    "Midjourney", "DALL-E 3", "Stable Diffusion 3",
    "Ideogram", "Flux", "Runway Gen",
    "Pika Labs", "Kling AI", "Sora",
    # AI 产品/平台（影响产品决策）
    "ChatGPT plugin", "GPT Store", "Claude Artifacts",
    "Gemini Advanced", "Perplexity",
    "Anthropic MCP", "OpenAI Codex",
]

EXACT_PRODUCT = [
    # 产品方法论专有名词
    "Jobs to be Done", "JTBD",
    "Product-Led Growth", "PLG",
    "product-market fit", "PMF",
    "Design Sprint",
    "Continuous Discovery",
    "Shape Up",
    "Double Diamond",
    "HEART framework",
]

EXACT_DESIGN = [
    # 设计系统/规范（不会误命中）
    "Material Design 3", "Human Interface Guidelines",
    "Ant Design", "Arco Design",
    "Design Tokens", "Figma Variables",
    "Auto Layout", "Figma Dev Mode",
    # 设计领域专有概念
    "Liquid Glass",  # Apple 新设计语言
    "Spatial Computing",
    "Apple Vision Pro",
]

EXACT_BUSINESS = [
    # 投资机构和加速器（命中 = 融资/行业信号）
    "Y Combinator", "a16z", "Sequoia",
    "Lightspeed", "Accel", "Benchmark",
    # 关键平台/生态
    "Product Hunt launch",
    "App Store", "Google Play",
]

EXACT_TECH = [
    # 具体模型名（不是泛称"AI"）
    "GPT-4o", "GPT-5", "Claude Opus", "Claude Sonnet",
    "Gemini 2", "Gemini Flash", "Gemma 3",
    "Llama 4", "Qwen 3", "DeepSeek",
    "Mistral Large", "Command R+",
    # 具体技术概念（不是泛称"技术"）
    "function calling", "tool use",
    "MCP protocol", "MCP server",
    "context window 1M",
    "chain of thought", "reasoning model",
    "vision model", "multimodal model",
    "on-device model", "edge inference",
]


# ============================================================
# 第二层: 短语匹配 — 2-4 词组合，描述特定话题
# 比单个词精准得多
# ============================================================

PHRASE_CORE = [
    # AI × 设计交叉（最高价值话题）
    "AI design tool", "AI 设计工具",
    "AI generate UI", "AI 生成界面",
    "AI prototype", "AI 原型",
    "text to UI", "text to design", "text to code",
    "prompt to design", "prompt to UI",
    "design copilot", "设计副驾驶",
    "AI wireframe", "AI 线框图",
    "AI layout generation", "AI 自动排版",
    "vibe coding", "自然语言编程",
    "AI code editor", "AI 代码编辑器",
    "conversational UI", "对话式界面",
    "language user interface", "语言界面",
    "agent workflow", "agent 工作流",
    "AI agent loop", "AI 代理循环",
    "agentic design", "代理式设计",
    "design automation", "设计自动化",
    "AI accessibility", "AI 无障碍",
]

PHRASE_PRODUCT = [
    # 产品方法论（具体方法名，不是泛称）
    "product discovery habit", "持续发现习惯",
    "assumption testing", "假设验证",
    "opportunity solution tree",
    "north star metric", "北极星指标",
    "activation rate", "激活率",
    "retention curve", "留存曲线",
    "onboarding flow", "引导流程",
    "user interview", "用户访谈",
    "value proposition canvas",
    "lean canvas",
    "pricing experiment", "定价实验",
    "freemium conversion", "免费转付费",
    "churn analysis", "流失分析",
    "feature adoption", "功能采纳率",
    "product sense", "产品感觉",
    "product critique", "产品拆解",
]

PHRASE_DESIGN = [
    # 体验设计（具体实践，不是泛称"设计"）
    "design system update", "设计系统更新",
    "component library", "组件库",
    "information architecture", "信息架构",
    "cognitive load reduction", "降低认知负担",
    "progressive disclosure", "渐进式披露",
    "micro-interaction", "微交互",
    "motion design principle", "动效设计原则",
    "dark pattern", "暗模式",
    "accessibility audit", "无障碍审查",
    "usability testing", "可用性测试",
    "heuristic evaluation", "启发式评估",
    "responsive redesign", "响应式改版",
    "design critique", "设计评审",
    "UX research finding", "用研发现",
    "user journey map", "用户旅程图",
    "design handoff", "设计交付",
]

PHRASE_BUSINESS = [
    # 商业（具体事件类型，不是泛称"商业"）
    "Series A funding", "A轮融资",
    "Series B funding", "B轮融资",
    "seed round", "种子轮",
    "acqui-hire", "人才收购",
    "design tool acquisition", "设计工具收购",
    "SaaS pricing change", "SaaS 定价调整",
    "ARR milestone", "ARR 里程碑",
    "unit economics", "单位经济模型",
    "LTV CAC ratio", "LTV CAC 比率",
    "product-led growth", "产品驱动增长",
    "bottom-up SaaS",
    "usage-based pricing", "按量付费",
    "AI wrapper business", "AI 套壳生意",
    "AI startup pivot",
    "platform risk", "平台风险",
]

PHRASE_TECH = [
    # 技术（具体能力/变化，不是泛称"技术"）
    "context window expand", "上下文窗口扩展",
    "inference cost drop", "推理成本下降",
    "open source model release", "开源模型发布",
    "model benchmark", "模型评测",
    "fine-tuning guide", "微调教程",
    "RAG pipeline", "RAG 管道",
    "embedding model", "向量模型",
    "prompt engineering technique", "提示工程技巧",
    "structured output", "结构化输出",
    "AI API update", "AI API 更新",
    "no-code AI", "无代码 AI",
    "low-code platform", "低代码平台",
    "AI native app", "AI 原生应用",
    "model distillation", "模型蒸馏",
]


# ============================================================
# 第三层: 组合匹配 — 两个词同时出现才算命中
# 解决单个泛词噪音太大的问题
# ============================================================

COMBO_KEYWORDS = [
    # ("词A", "词B") → 两个都出现才命中
    # 解决: "AI" 单独出现噪音太大，但 "AI" + "设计" 就精准了
    ("AI", "designer workflow"),
    ("AI", "design system"),
    ("AI", "UX research"),
    ("AI", "prototyping"),
    ("AI", "Figma"),
    ("AI", "user experience"),
    ("AI", "interaction design"),
    ("AI", "product manager"),
    ("AI", "产品经理"),
    ("AI", "设计师"),
    ("AI", "交互设计"),
    ("AI", "用户体验"),
    # "open source" 太泛，但 "open source" + "design" 就有价值
    ("open source", "design tool"),
    ("open source", "设计工具"),
    # "pricing" 太泛，但 "pricing" + "AI tool" 就是你读者关心的
    ("pricing", "AI tool"),
    ("pricing", "design tool"),
    ("pricing", "SaaS"),
    # "launch" 太泛，但 "launch" + "Product Hunt" 就精准
    ("launch", "Product Hunt"),
    ("launch", "AI tool"),
    # "update" 太泛，但 "update" + 具体工具名就精准
    ("update", "Figma"),
    ("update", "Cursor"),
    ("update", "Framer"),
    ("update", "Notion"),
    ("release", "Figma"),
    ("release", "Cursor"),
]


# ============================================================
# 权重配置
# ============================================================

KEYWORD_WEIGHTS = {
    "exact_core": 4.0,       # 精确命中核心工具名 — 最高
    "exact_product": 2.5,
    "exact_design": 2.5,
    "exact_business": 2.0,
    "exact_tech": 1.5,
    "phrase_core": 3.5,      # 短语命中 — 次高
    "phrase_product": 2.0,
    "phrase_design": 2.0,
    "phrase_business": 1.5,
    "phrase_tech": 1.0,
    "combo": 3.0,            # 组合命中 — 高（因为更精准）
}

ALL_WHITELISTS = {
    "exact_core": EXACT_CORE,
    "exact_product": EXACT_PRODUCT,
    "exact_design": EXACT_DESIGN,
    "exact_business": EXACT_BUSINESS,
    "exact_tech": EXACT_TECH,
    "phrase_core": PHRASE_CORE,
    "phrase_product": PHRASE_PRODUCT,
    "phrase_design": PHRASE_DESIGN,
    "phrase_business": PHRASE_BUSINESS,
    "phrase_tech": PHRASE_TECH,
}


# ============================================================
# 匹配函数
# ============================================================

def calculate_relevance(title: str, summary: str) -> tuple:
    """
    计算一条资讯的白名单相关性分数。
    
    三层匹配逻辑:
    1. exact: 精确工具名/专有名词
    2. phrase: 2-4词组合短语
    3. combo: 两个词同时出现
    
    Returns: (score, matched_keywords)
    """
    text = (title + " " + summary).lower()
    score = 0.0
    matched = []

    # Layer 1 & 2: exact + phrase 匹配
    for category, keywords in ALL_WHITELISTS.items():
        weight = KEYWORD_WEIGHTS[category]
        for kw in keywords:
            if kw.lower() in text:
                score += weight
                matched.append((category, kw))

    # Layer 3: combo 匹配
    for word_a, word_b in COMBO_KEYWORDS:
        if word_a.lower() in text and word_b.lower() in text:
            score += KEYWORD_WEIGHTS["combo"]
            matched.append(("combo", f"{word_a} + {word_b}"))

    return score, matched
