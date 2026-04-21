# 成果定义

## 主输出

| 文件 | 说明 |
|------|------|
| `data/output/{DATE}-dialogue-xfyun.mp3` | 讯飞主路径（`python -m tools.article_tts`） |
| `data/output/{DATE}-dialogue-*.mp3` | 备选 `tts_dialogue` 各 preset |

## 输入依赖

| 文件 | 说明 |
|------|------|
| `data/output/{DATE}-article.md` | **唯一**朗读正文来源 |

## 已废弃的平行产出（勿再作为正式交付）

- ~~`{DATE}-dialogue.md`~~：与 `article.md` 重复的第二对话稿。新流程下 **不生成** 或与 `article.md` 内容重复时仅保留 `article.md`。

## 验收检查项

- [ ] 音频由 `article.md` 生成，而非单独从 `briefing.md` 写一篇新对话再录  
- [ ] 角色分轨/音色符合项目配置（若适用）  
- [ ] 时长与断句适合口播（可按 `article-dialogue-tts` skill / 讯飞参数调整）
