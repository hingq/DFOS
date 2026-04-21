# Background

## 任务定位

**Briefing Article Agent** 将 `processing.json` 中的结构化资讯，**合成为一篇对话式结构的长文**，输出为 `data/output/{DATE}-article.md`。

该产出与 **Daily Briefing** 的 `briefing.md` 分工明确：

| 产出 | 角色 |
|------|------|
| `briefing.md` | 短讯列表 + 编辑视角，5 分钟扫读 |
| `article.md` | 对话式深度稿，**唯一**口播/TTS 母本 |

## 信息源

- **主输入**：`data/intermediate/{DATE}-processing.json`  
- **可选**：`data/output/{DATE}-briefing.md`（对齐当日口径）  
- **可选**：`product-research`、多源检索摘要（外源观点需标注立场与来源）

## 处理流程

1. 读取 `processing.json`，按 `tier` / `final_score` / `category` 取舍条目。  
2. 按 **briefing-article-style** skill 组织对话式章节与角色。  
3. 写入 `data/output/{DATE}-article.md`。

## 与其他 Agent 的关系

- **依赖**：`daily-briefing-agent` 的 `processing` 结果  
- **下游**：`dialogue-briefing-agent` **仅**读取本 `article.md` 生成音频（不生成第二份长文）
