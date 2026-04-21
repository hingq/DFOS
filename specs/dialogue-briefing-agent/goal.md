# 目标

## 交付成果

1. **音频文件（主交付）**：`data/output/YYYY-MM-DD-dialogue-xfyun.mp3`（讯飞，`python -m tools.article_tts`）或 `dialogue-*.mp3`（`tts_dialogue` 备选）  
   - **唯一朗读母本**：`data/output/YYYY-MM-DD-article.md`（由 Briefing Article Agent 产出的对话式结构化文章）  
   - 使用 TTS（主：科大讯飞；备选：Edge 等，见 `article-dialogue-tts` skill 与 `tools/tts_dialogue`）

2. **不再单独交付**：~~`YYYY-MM-DD-dialogue.md` 作为与 `article.md` 平行的第二篇长对话~~。若历史脚本仍生成 `dialogue.md`，应迁移为 **仅由 `article.md` 驱动音频**，避免双轨正文。

## 核心要求

1. **输入唯一性**：语音脚本必须基于 **`article.md`**，不得再从 `briefing.md` 独立生成一篇长对话作为口播主稿。  
2. **角色配音**：`article.md` 中 **`Q` / `A`**（或历史 **Qearl**）：**Q 男声、A 女声**，与 `article-dialogue-tts` / `XFYUN_VCN_*` 或 `tts_dialogue` preset 一致。  
3. **可选预处理**：仅允许对 `article.md` 做口播友好微调（断句、停顿标记），**不改变事实与观点**；微调结果可写临时文件或仍回写规范见团队约定。

## 与 Briefing Article 的分工

| Agent | 产出 |
|-------|------|
| Briefing Article | `article.md` = 对话式正文 + 口播母本 |
| Dialogue Briefing（本 Agent） | `*.mp3`（及可选口播脚本中间件） |
