# Background

## 任务定位

**Product Research Agent** 对指定 **AI 产品或设计工具** 做结构化深度调研，产出可复用的 **Product Profile**（YAML + Markdown + 来源清单），供步骤 3 长文引用、竞品对比或独立归档。

## 与主流程的关系

| 阶段 | 关系 |
|------|------|
| 步骤 2 日报 | 可从 `processing.json` / `briefing.md` 中选定产品名再启动本 Agent |
| 步骤 3 结构化文章 | 可将本 Agent 产出的 facts / 来源 **摘要后并入** `article.md`，不替代口播母本 |

## 信息源优先级（可信度递减）

1. 官方：官网、文档、定价页、发布博客、Status 页  
2. 一手报道：权威科技媒体、官方署名稿  
3. 社区：Twitter/X、Reddit、HN、Product Hunt 评论（需标注为二手观点）  
4. 检索：multi-search / web_fetch；**不得**把未核实传闻写进事实字段

## 工具

- **multi-search** skill、**autocli**（需登录站）  
- 浏览器与 API 以团队当前配置为准

## 输出根目录

默认：`data/output/product-profiles/{slug}/`（`slug` 为小写产品名或短标识，见 `output.md`）。
