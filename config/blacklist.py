"""关键词黑名单

硬黑名单：命中直接丢弃
软黑名单：命中降权但不直接丢弃
"""

BLACKLIST_HARD = [
    # 与主题无关的领域
    "自动驾驶", "autonomous driving", "self-driving",
    "量化交易", "algorithmic trading", "quant",
    "加密货币", "cryptocurrency", "crypto", "blockchain",
    "Web3", "NFT", "DeFi", "元宇宙", "metaverse",
    "挖矿", "mining rig",
    # 纯学术
    "arxiv paper", "peer review", "ICML", "NeurIPS", "ICLR",
    "protein folding", "蛋白质折叠",
    "drug discovery", "药物发现",
    "genomics", "基因组学",
    # 垃圾内容
    "震惊", "颠覆", "必看", "不转不是",
    "月入过万", "副业赚钱", "暴富", "躺赚",
    "限时免费", "仅剩最后", "名额有限",
    "casino", "gambling", "porn", "adult",
    "forex", "外汇", "二元期权",
    # 无关硬件
    "智能家居", "smart home", "IoT sensor",
    "3D打印", "3D printing",
    "无人机", "drone",
    "芯片制造", "chip fabrication",
    # AI 炒作
    "AI will replace", "AI 将取代所有",
    "AGI is coming", "singularity", "奇点",
    "AI consciousness", "AI 意识",
]

BLACKLIST_SOFT = [
    # 工具罗列
    "10个AI工具", "10 AI tools", "best AI tools list",
    "工具合集", "tools roundup", "ultimate list",
    "XX个免费", "free tools collection",
    "2026年最佳", "best of 2026",
    # 过度入门
    "什么是AI", "what is AI", "AI for beginners",
    "什么是机器学习", "入门指南", "beginner's guide",
    "如何开始学习", "how to get started",
    # 企业 PR
    "press release", "新闻稿",
    "we're excited to announce", "我们很高兴宣布",
    "customer story", "客户案例",
    # 泛科技
    "iPhone", "Android update", "系统更新",
    "gaming", "游戏", "esports", "电竞",
    "streaming", "直播",
    "电商大促", "双十一", "黑五",
    # 招聘
    "hiring", "招聘", "job opening", "职位",
    "salary", "薪资",
    # 二手聚合
    "weekly digest", "每周精选",
    "月度总结", "monthly recap",
    "年度回顾", "year in review",
]


def should_discard(title: str, summary: str) -> tuple:
    """硬黑名单检查。返回 (是否丢弃, 原因)"""
    text = (title + " " + summary).lower()
    for kw in BLACKLIST_HARD:
        if kw.lower() in text:
            return True, f"硬黑名单: {kw}"
    return False, ""


def calculate_penalty(title: str, summary: str) -> float:
    """软黑名单降权系数。1.0=不降权，越低越降"""
    text = (title + " " + summary).lower()
    penalty = 1.0
    for kw in BLACKLIST_SOFT:
        if kw.lower() in text:
            penalty *= 0.5
    return max(penalty, 0.1)
