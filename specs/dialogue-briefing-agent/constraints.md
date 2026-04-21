# 约束

## 负向约束（严禁）

- **严禁**以 `briefing.md` 为唯一输入再写一篇长对话，替代 `article.md` 作为口播主稿。  
- **严禁**与 Briefing Article 产出的 `article.md` 在事实与观点上不一致（音频层仅做格式与停顿优化）。  
- **严禁**双正文：不得同时维护两篇不同对话长文（`article` vs `dialogue`）作为并行交付。

## 正向约束

- **必须先存在** `data/output/{DATE}-article.md`，再生成音频。  
- 口播优化若需中间文件，须在 spec 或文档中命名，避免与正式 `article.md` 混淆。

## 音频生成

- 使用项目配置的 TTS（见 `.claude/CLAUDE.md` 与 `tts` skill）。  
- 分角色配音时与 `article.md` 中的说话人一致。
