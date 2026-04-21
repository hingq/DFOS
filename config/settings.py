"""全局配置"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 路径
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MANUAL_DIR = DATA_DIR / "manual"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
OUTPUT_DIR = DATA_DIR / "output"
CONTEXT_DIR = PROJECT_ROOT / "context"
LOG_DIR = PROJECT_ROOT / "logs"

# 简报 HTML：模板与 CSS 唯一源在 briefing-html-style skill；构建产物在 web/dist/
WEB_DIR = PROJECT_ROOT / "web"
WEB_DIST_DIR = WEB_DIR / "dist"
WEB_DIST_STATIC_DIR = WEB_DIST_DIR / "static"
WEB_DIST_BRIEFING_DIR = WEB_DIST_DIR / "briefing"

BRIEFING_HTML_SKILL_DIR = PROJECT_ROOT / ".claude" / "skills" / "briefing-html-style"
BRIEFING_HTML_ASSETS_DIR = BRIEFING_HTML_SKILL_DIR / "assets"
BRIEFING_HTML_TEMPLATE = BRIEFING_HTML_ASSETS_DIR / "briefing_shell.html"
BRIEFING_HTML_CSS_SOURCE = BRIEFING_HTML_ASSETS_DIR / "briefing.css"

# 确保目录存在
for d in [
    RAW_DIR,
    MANUAL_DIR,
    INTERMEDIATE_DIR,
    OUTPUT_DIR,
    LOG_DIR,
    WEB_DIST_STATIC_DIR,
    WEB_DIST_BRIEFING_DIR,
]:
    d.mkdir(parents=True, exist_ok=True)

# LLM：优先 Anthropic 官方，其次 MiniMax 兼容
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_ANTHROPIC_BASE_URL = os.getenv(
    "MINIMAX_ANTHROPIC_BASE_URL",
    "https://api.minimax.io/anthropic",
)
# 兼容层支持的模型示例：MiniMax-M2.7、MiniMax-M2.5、MiniMax-M2.1、MiniMax-M2 等
LLM_MODEL = os.getenv("LLM_MODEL", "MiniMax-M2.5")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# 通知
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
WECHAT_WEBHOOK = os.getenv("WECHAT_WEBHOOK", "")
BARK_TOKEN = os.getenv("BARK_TOKEN", "")

# Autocli
AUTOCLI_URL = os.getenv("AUTOCLI_URL", "")

# Pipeline 参数
MAX_RAW_ITEMS = 50          # 单次抓取最大条数
MAX_LLM_INPUT = 30          # 送入 LLM 的最大条数
BRIEFING_MUST_READ = 3      # "今日必看" 最大条数
BRIEFING_WORTH_NOTING = 6   # "值得关注" 最大条数
BRIEFING_TOOL_RADAR = 3     # "工具雷达" 最大条数

# 值得深挖：近 N 天 raw 频次统计（与 pipeline/deep_dive.py 一致）
DEEP_DIVE_SIGNAL_DAYS = int(os.getenv("DEEP_DIVE_SIGNAL_DAYS", "7"))

# Twitter / X 对简报权重（与 pipeline/source_utils + prefilter 配合）
# 预过滤阶段：命中 Twitter 的条目在关键词分上乘以该系数，便于进入评分池
TWITTER_PREFILTER_BOOST = 1.35
# 进入 LLM 6 维评分的最大条数（原 5 过窄，易挤掉 Twitter）
SCORING_POOL_SIZE = 10
# 评分池中至少保证几条 Twitter 素材（若预过滤后仍有）；0 表示不强制
MIN_TWITTER_IN_SCORING_POOL = 2
# 评分后：若条目为 Twitter 且 tier 已入围，对 final_score 做小幅加成（便于同档排序与展示侧重）
TWITTER_FINAL_SCORE_BONUS = 0.08


def load_context(filename: str) -> str:
    """加载 context 文件内容"""
    filepath = CONTEXT_DIR / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return ""
