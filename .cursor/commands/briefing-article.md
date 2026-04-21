# Briefing Article（步骤 3：单产品对话式长文）

生成 **`data/output/YYYY-MM-DD-article.md`**：口播母本，**一篇只围绕一个 AI 产品/工具**做对话式全量分析。

## 语义说明

| 术语 | 含义 |
|------|------|
| **article** | **单产品**对话式长文（李达达 / Qearl），**不是**列表式简报 |
| **briefing** | 步骤 2 的短讯列表 `*-briefing.md`，与 article **分工不同** |

## 执行步骤

1. 阅读 `specs/daily-briefing-article-agent/` 下全部 spec（可选 `product-research-agent` 若需补素材）
2. 确认已有 `data/intermediate/YYYY-MM-DD-processing.json`（须先跑完步骤 2）
3. 运行生成脚本（选题由代码自动完成，见 `pipeline/article_pick.py`）：

```bash
python -m tools.generate_article
# 或指定日期
python -m tools.generate_article --date YYYY-MM-DD
# 或
BRIEFING_DATE=YYYY-MM-DD python -m tools.generate_article
```

4. 体裁、结构、禁忌见 **`.claude/skills/briefing-article-style/SKILL.md`**（须与脚本一致：**只写一条选题**）

## 输出

- `data/output/YYYY-MM-DD-article.md`

## 约束

- **不要**用 `briefing.md` 替代 `processing.json` 作为唯一事实源；脚本是基于 processing 选题并生成
- 人工改稿时若更换主题，仍须保持**单产品深度**与对话结构
