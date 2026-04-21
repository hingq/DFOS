# Dialogue Briefing（步骤 4：仅 TTS）

**dialogue** 在本项目中专指：**把已有文字稿转成语音**，**不是**再写一篇对话文章。

| 术语 | 含义 |
|------|------|
| **article** | 步骤 3 产出的 `*-article.md`（单产品对话式口播母本） |
| **dialogue-briefing** | **仅音频**：输入 = article，输出 = `*.mp3` |

## 执行步骤

1. 阅读 `specs/dialogue-briefing-agent/` 下全部 spec
2. 确认已存在 **`data/output/YYYY-MM-DD-article.md`**（须先完成步骤 3）
3. 使用 TTS（**不要**从 `briefing.md` 生成第二篇长对话再录）：

```bash
# 主路径：科大讯飞（需 XFYUN_* 环境变量，见 article-dialogue-tts skill）
python3 -m tools.article_tts
BRIEFING_DATE=YYYY-MM-DD python3 -m tools.article_tts --date YYYY-MM-DD

# 备选：Edge / 其他预设（无需讯飞）
python3 -m tools.tts_dialogue --list-presets
BRIEFING_DATE=YYYY-MM-DD python3 -m tools.tts_dialogue --preset edge
```

4. Skill：**`.claude/skills/article-dialogue-tts/SKILL.md`**；密钥与发音人见其中 `references/what-you-provide.md`

## 输出

- 讯飞默认：`data/output/YYYY-MM-DD-dialogue-xfyun.mp3`
- `tts_dialogue`：`data/output/YYYY-MM-DD-dialogue-*.mp3`（依 `--preset`）

## 约束

- **严禁**以 `briefing.md` 为口播主稿替代 `article.md`
- 路径约定以 `tools/tts_paths.py` 为准；主入口 `python -m tools.article_tts`；旧 `tools/generate_dialogue_*.py` 为 shim
