# Goal

## 交付成果

产出一篇 **对话式结构的行业长文** Markdown，路径固定为：

- `data/output/{DATE}-article.md`

该文件同时满足：

1. **可读发布**：对话式分节（如开场、主题讨论、结尾；或主持/分析师 Q&A），有观点碰撞与编辑判断。  
2. **口播母本**：作为 **TTS / 语音生成的唯一正文来源**；不再要求另存一份平行的「第二对话长文」。

## 验收标准

1. **体裁**  
   - 遵循项目 **`.claude/skills/briefing-article-style/SKILL.md`** 中的结构、角色与风格约束。  
   - 可与 `context/style.md`、`context/viewpoint.md`、`context/expectations.md` 对齐。

2. **选题与覆盖**  
   - **单篇聚焦一个对象**：自动化选题由 **`pipeline/article_pick.py`** 从 `processing.json` 中选一条（优先 `new_tool` → `tier` → `final_score`）；`tools/generate_article.py` 已使用该逻辑。人工指定主题时仍以单产品深度为准。  
   - 可选：引用 **product-research-agent** 产出、`multi-search` 外源作补充，须在正文中区分事实与二手观点。

3. **篇幅**  
   - 建议 1500–4000 字（可按 skill 微调），以口播可完成为准。

4. **禁止**  
   - 不得再单独生成一份与本文并行的「从 briefing 重写的对话稿」；pipeline 已移除 `briefing-chat.md` 与 `generate_dialogue_from_briefing.py` 路径。
