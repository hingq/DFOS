"""按旧脚本规则为句首加语气词（可选）。"""
from __future__ import annotations

from typing import Callable

PrefixFn = Callable[[int, str, str], str]

MAX_SEGMENT = 500


def _truncate(s: str) -> str:
    return s[:MAX_SEGMENT] if len(s) > MAX_SEGMENT else s


def prefix_none(_i: int, _speaker: str, content: str) -> str:
    return _truncate(content)


def prefix_audio2(_i: int, speaker: str, content: str) -> str:
    c = content.strip()
    if "Qearl" in speaker:
        c = "嗯，" + c if not c.startswith("嗯") else c
    else:
        c = "那个，" + c if not c.startswith("那个") else c
    return _truncate(c)


def prefix_audio4(_i: int, speaker: str, content: str) -> str:
    c = content.strip()
    if "Qearl" in speaker:
        if not c.startswith(("嗯", "那", "这个", "所以", "我")):
            c = "那什么，" + c
    else:
        if not c.startswith(("嗯", "那个", "所以", "我")):
            c = "那个，" + c
    return _truncate(c)


def prefix_sparse_edge(i: int, speaker: str, content: str) -> str:
    c = content.strip()
    if "Qearl" in speaker:
        if not c.startswith(("嗯", "那", "这个", "所以", "我", "其实", "但是")):
            if i % 10 < 2:
                c = "那什么，" + c
    else:
        if not c.startswith(("嗯", "那个", "所以", "我", "其实", "但是", "对")):
            if i % 10 < 2:
                c = "那个，" + c
    return _truncate(c)


def prefix_sparse_noiz(i: int, speaker: str, content: str) -> str:
    """与 `generate_dialogue_noiz` 一致。"""
    return prefix_sparse_edge(i, speaker, content)


def prefix_guest_audio3(_i: int, speaker: str, content: str) -> str:
    """与 `generate_dialogue_audio3` 一致。"""
    c = content.strip()
    if "Qearl" in speaker:
        prefix = "那什么，"
        if not c.startswith(("嗯", "那", "这个", "所以", "我")):
            c = prefix + c
    else:
        prefix = "嗯，"
        if not c.startswith(("嗯", "那", "这个", "所以", "我")):
            c = prefix + c
    return _truncate(c)


PREFIX_REGISTRY: dict[str, PrefixFn] = {
    "none": prefix_none,
    "audio2": prefix_audio2,
    "audio4": prefix_audio4,
    "sparse_edge": prefix_sparse_edge,
    "sparse_noiz": prefix_sparse_noiz,
    "guest_audio3": prefix_guest_audio3,
}
