# 背景

## 任务定位

**Dialogue Briefing Agent** 负责将 **Briefing Article** 已写好的 **`article.md`** 转为 **音频**。  

历史上本 Agent 曾从 `briefing.md` 单独生成 `dialogue.md`；按现行架构，**对话式正文已合并进 `article.md`**，本 Agent **仅负责声音层**，不再承担「第二篇对话长文」的写作职责。

## 与 Daily Briefing 的区别

| 类型 | 文件 | 作用 |
|------|------|------|
| Daily Briefing | `briefing.md` | 当日短讯简报 |
| Briefing Article | `article.md` | 对话式深度稿 + **唯一**口播母本 |
| Dialogue Briefing | `*.mp3` | 朗读 `article.md` |

## 信息源

- **输入**：`data/output/YYYY-MM-DD-article.md`（必选）  
- **上下文**：`context/portrait.md`、`context/style.md`（角色与语气，与 article 内角色一致即可）

## 可用工具

- **TTS（主）**：`python -m tools.article_tts`（科大讯飞；环境变量见 skill）  
- **TTS（备选）**：`python -m tools.tts_dialogue`（`--preset edge` 等；旧脚本为 shim）  
- **Skill**：`.claude/skills/article-dialogue-tts/SKILL.md`
