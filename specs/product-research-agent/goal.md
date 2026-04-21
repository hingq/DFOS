# Goal

## 交付成果

在 `data/output/product-profiles/{slug}/` 下产出：

1. **`{slug}.yaml`** — 结构化 Product Profile（机器可读）  
2. **`{slug}.md`** — 人类可读摘要报告（含评估与 SWOT 风格段落）  
3. **`sources.md`** — 来源列表（URL + 一句用途 + 访问日期）

## Profile Schema（YAML 顶层字段）

| 字段 | 说明 |
|------|------|
| `name` | 产品正式名称 |
| `company` | 公司 / 团队 |
| `one_liner` | 一句话定位 |
| `category` | 如：设计工具、编码 Agent、图像生成… |
| `pricing` | 定价摘要；未公开写 `未公开` |
| `key_features` | 列表：核心能力 |
| `integrations` | 列表：集成 / 生态 |
| `differentiation` | 与常见替代品的差异（简述） |
| `risks` | 风险或限制（依赖、隐私、合规等） |
| `assessment` | 短评：机会与威胁（可与 `context/excellent.md` 对齐） |
| `last_researched` | `YYYY-MM-DD` |

## 验收标准

- 每个关键事实在 `sources.md` 中可追溯到 URL  
- 定价以**官网定价页**为准；未找到则 `未公开`  
- 不编造融资额、用户数、功能列表
