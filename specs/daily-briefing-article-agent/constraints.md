# Constraints

## 内容约束

- 不用「震惊」「重磅」「颠覆」等营销词（除非引述并加引号）。  
- 不整段复制原文；外源观点需转述并归属。  
- 编辑视角须有产品判断，不能仅复述事实。

## 体裁约束

- **必须**为对话式结构（见 `briefing-article-style` skill）。  
- **禁止**另存一份与 `article.md` 同目的的平行长对话文件。

## 运行约束

- 主输入：`data/intermediate/{DATE}-processing.json`  
- 输出：`data/output/{DATE}-article.md`  
- 不擅自修改 `pipeline/prompts/scoring.py` 权重
