"""日报口播：从 `*-article.md` 按 Q/A 调用讯飞流式 TTS，合并为单文件 MP3。

统一入口：`python -m tools.article_tts`
"""

from __future__ import annotations

from tools.article_tts.runner import run_article_tts

__all__ = ["run_article_tts"]
