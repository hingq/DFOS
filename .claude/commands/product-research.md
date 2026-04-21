# 产品调研

对指定的 AI 产品进行深度调研，生成结构化的产品档案。

## 执行流程

### 第一步：读取调研规范

阅读以下 spec 文件，理解调研标准：

```
specs/product-research-agent/background.md  → 信息源和采集策略
specs/product-research-agent/goal.md        → Product Profile Schema
specs/product-research-agent/constraints.md → 约束和质量门槛
specs/product-research-agent/output.md      → 输出格式和验收标准
```

### 第二步：信息采集

按 constraints.md 中的优先级顺序采集：

1. **搜索产品基本信息**：用 multi-search skill 搜索产品名
2. **访问产品官网**：用 web_fetch 读取 landing page、pricing page、changelog
3. **搜索媒体报道**：搜索 "[产品名] funding"、"[产品名] review"
4. **搜索用户反馈**：搜索 "[产品名] Twitter"、"[产品名] Reddit"
5. **搜索竞品信息**：搜索 "[产品名] vs"、"[产品名] alternatives"

### 第三步：填充 Profile Schema

按 goal.md 中的 schema 结构，逐字段填充。不确定的字段标注「未公开」。

### 第四步：生成评估

参考 `context/excellent.md` 中的好产品标准，撰写 assessment 部分（SWOT + outlook）。

### 第五步：输出

1. 生成 YAML：`data/output/product-profiles/{slug}/{slug}.yaml`
2. 生成 Markdown：`data/output/product-profiles/{slug}/{slug}.md`
3. 生成来源汇总：`data/output/product-profiles/{slug}/sources.md`

## 约束

- 严格按 spec 中的 schema 和约束执行
- 不编造任何信息，不确定就写「未公开」
- 每个关键事实标注来源
- 定价信息必须来自官方定价页
