---
name: daily-review
description: 每日简报审核与发布。当用户说「审核日报」「review」「看看今天的简报」「检查一下日报」「发布日报」「今天的日报怎么样」时触发。自动运行质量检查脚本，读取简报内容和评分数据，逐项审核并输出结果。即使用户只是说"日报好了吗"也应该触发此 skill。
---

# 每日审核 Skill

自动检查日报质量，辅助 5-10 分钟的人工审核。

## 触发条件

- 用户说「审核日报」「审核今天的日报」
- 用户说「review」「review today」
- 用户说「看看今天的简报」「日报好了吗」
- 用户说「检查一下日报」「check briefing」
- 用户说「发布日报」「publish」

## 工具依赖

- 终端: 执行 `.claude/skills/daily-review/scripts/review-checker.py`（项目根目录下）
- 文件系统: 读取 `data/output/`, `data/intermediate/`

## 操作步骤

### 步骤 1: 运行自动检查脚本

```bash
python .claude/skills/daily-review/scripts/review-checker.py
```

该脚本自动执行 5 项检查：

| 检查项 | 做什么 | 输出 |
|--------|--------|------|
| 头条排序 | 最高分条目是否在第一位 | ✅ pass 或 ⚠️ 建议调换 |
| 评分分布 | must_read/worth_noting/tool_radar 数量是否合理 | 各层级计数 + 异常警告 |
| 分类覆盖 | 5个分类（new_tool/case_study/trend/methodology/opinion）覆盖几个 | 已覆盖/缺失分类 |
| 实体统计 | 提取了多少产品名和公司名 | Top 产品/公司排名 |
| 简报长度 | 字数和段落数是否合理 | 过长/过短警告 |

### 步骤 2: 读取简报内容

```bash
cat data/output/$(date +%Y-%m-%d)-briefing.md
```

将简报完整内容展示给用户。

### 步骤 3: 针对警告项逐一处理

根据脚本输出的警告，执行对应的修正：

**头条不对 →**
```
读取 data/intermediate/YYYY-MM-DD-scoring.json，
找出 final_score 最高的条目，
在 briefing.md 中将其移到"今日必看"第一位。
```

**评分分布异常 →**
```
如果 must_read 过多(>3)：降级得分最低的几条到 worth_noting
如果 must_read 为 0：检查是否有条目被误评低分
如果总量过多(>15)：砍掉最低分的条目
```

**编辑视角质量 →**
```
读取简报中「编辑视角」段落。
判断标准：
- 是否只是复述事实（不够）
- 是否有产品架构师角度的判断（需要）
- 是否关联了 context 中的框架

如果不够锐利，参考以下文件重写：
  context/viewpoint.md   → 理论依据
  context/excellent.md   → 好产品标准
  context/methodology.md → 分析框架
```

### 步骤 4: 事实核查

逐条扫描简报中的关键事实：

```
对每条 source_url:
1. 用 multi-search skill 或 web_fetch 打开原文
2. 核对产品名、公司名、数据是否一致
3. 发现错误则直接在 briefing.md 中修正
```

仅在用户要求或发现可疑信息时执行此步骤。日常可跳过。

### 步骤 5: 记录审核日志

审核完成后：

```bash
echo "$(date +%Y-%m-%d) | 编辑时间: X分钟 | 改动: [描述] | 原因: [原因]" >> docs/review-log.md
```

### 步骤 6: 输出审核报告

汇总所有检查结果，输出：

```markdown
## 审核结果: YYYY-MM-DD

✅/⚠️ 头条: [通过 / 建议换为 xxx]
✅/⚠️ 分布: [must_read N, worth_noting N, tool_radar N]
✅/⚠️ 分类: [覆盖 N/5]
✅/⚠️ 长度: [N lines, N chars]
📊 整体: 可发布 / 需修改

[如有修改项，列出具体改动]
```

## 脚本文件

| 文件 | 用途 |
|------|------|
| `scripts/review-checker.py` | 自动质量检查（头条/分布/分类/实体/长度）|

### review-checker.py 函数

| 函数 | 用途 |
|------|------|
| `run_review(date)` | 主入口：运行所有检查 |
| `check_headline(scoring)` | 头条排序是否正确 |
| `check_score_distribution(scoring)` | 评分分布是否合理 |
| `check_category_coverage(processing)` | 分类覆盖度 |
| `check_entities(processing)` | 实体提取统计 |
| `check_briefing_length(date)` | 简报长度检查 |

## 关联文件

| 文件 | 用途 |
|------|------|
| `data/output/YYYY-MM-DD-briefing.md` | 简报草稿 |
| `data/intermediate/YYYY-MM-DD-scoring.json` | 评分明细 |
| `data/intermediate/YYYY-MM-DD-processing.json` | 分类和实体 |
| `docs/review-log.md` | 审核日志 |
| `docs/prompt-changelog.md` | 评分偏差记录（发现偏差时写入）|
| `context/viewpoint.md` | 编辑视角参考 |
| `context/excellent.md` | 质量标准参考 |

## 完整示例

**用户输入**: 「审核今天的日报」

**执行流程**:
1. 运行 `python .claude/skills/daily-review/scripts/review-checker.py` → 输出自动检查结果
2. 读取 `data/output/YYYY-MM-DD-briefing.md` → 展示简报内容
3. 根据警告项提出修改建议
4. 用户确认后执行修改
5. 记录到 `docs/review-log.md`
6. 输出审核报告
