# Output

## 简报素材与交付

- **输入侧**：Twitter 采集与其他信源抓取 **合并** 进入 raw / pipeline（见 `background.md`）。  
- **交付侧**：简报 **Markdown 主稿**为 `data/output/YYYY-MM-DD-briefing.md`；**同一次 pipeline** 自动生成可浏览页 `web/dist/briefing/YYYY-MM-DD.html`（样式源：`.claude/skills/briefing-html-style/assets/`）。**勿**在 `data/output/` 保留或维护 `*-briefing.html`。  
- **已废弃**：不再生成 `*-briefing-chat.md`（旧「对话体简报」）；对话式长文见 `*-article.md`。

## 目录结构

```
data/
├── raw/YYYY-MM-DD-{source}.json           # 原始抓取（含多信源合流）
├── intermediate/YYYY-MM-DD-scoring.json   # 评分明细
├── intermediate/YYYY-MM-DD-processing.json # 分类+实体
└── output/YYYY-MM-DD-briefing.md          # 最终简报（Markdown）

web/dist/
├── briefing/YYYY-MM-DD.html               # 简报网页（构建产物）
└── static/briefing.css                    # 从 skill assets 复制
```

## 验收检查

运行 `python .claude/skills/daily-review/scripts/review-checker.py` 自动检查：
- 头条排序是否正确
- 评分分布是否合理
- 分类覆盖度
- 简报长度
