# 路径约定（与代码一致）

| 项目 | 路径 |
|------|------|
| 口播母本 | `data/output/{DATE}-article.md` |
| 默认输出音频 | `data/output/{DATE}-dialogue-xfyun.mp3` |
| 日期解析 | `tools/tts_paths.py`：`BRIEFING_DATE` 优先，否则当天 |

实现：`tools/article_tts/runner.py` 使用 `article_md_path`、`audio_output_path`。
