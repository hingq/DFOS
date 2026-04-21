# Constraints

## 诚信

- **不得编造**：价格、功能、发布日期、合作伙伴、数据指标  
- 不确定字段写 **`未公开`** 或 **`待核实`**，并在正文说明依据不足

## 范围

- 单次调研聚焦 **一个** 主产品；若需对比，另开 **Competitive Analysis** 或第二份 profile

## 与步骤 3 长文

- 本 Agent **不**产出 `article.md`；长文仍由 **Briefing Article** + `briefing-article-style` 生成  
- 可将 `profile.md` 中的段落 **摘要引用** 进 `article.md`，避免整篇粘贴

## 运行约束

- 不修改 `pipeline/prompts/scoring.py` 权重  
- 不将调研结果写回 `processing.json`（除非团队另有 ETL 流程）
