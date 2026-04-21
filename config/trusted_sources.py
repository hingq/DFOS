"""信任信源配置（方法二：预过滤直通评分池）

规则：
- 仅跳过「关键词/相关性门槛」；**硬黑名单仍然生效**。
- 每个 source 有单日进入合并池的条数上限，且所有信任源合计不超过 TRUSTED_POOL_MAX。
- RawItem.source 必须与爬虫 / sources.py 里的 name 一致（此处按**小写**匹配）。

新增信源时：在此 dict 增加一行即可，key 用 raw JSON 里的 source 字段小写形式。
"""

from __future__ import annotations

from typing import Dict

# 各信任源每日进入预过滤合并池的条数上限（防单源刷屏）
TRUSTED_SOURCE_LIMITS: Dict[str, int] = {
    # 手动录入：误杀成本高，默认直通
    "manual": 8,
}

# 信任源合计条数上限（在逐源 cap 之后仍可能截断）
TRUSTED_POOL_MAX = 10


def normalize_source_key(source: str) -> str:
    return (source or "").strip().lower()


def is_trusted_source(source: str) -> bool:
    return normalize_source_key(source) in TRUSTED_SOURCE_LIMITS


def trusted_limit_for(source: str) -> int:
    return TRUSTED_SOURCE_LIMITS.get(normalize_source_key(source), 0)
