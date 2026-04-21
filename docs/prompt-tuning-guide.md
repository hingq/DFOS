---
name: prompt-tuning
description: Prompt 调优流程。当用户说「调一下 prompt」「优化评分」「简报质量不好」「这条不应该评这么高/低」「改一下生成模板」时触发。分析历史审核数据定位问题，执行最小改动，验证效果。
---

# Prompt 调优 Skill

基于审核反馈迭代 pipeline 中的 3 个 LLM prompt。

## 触发条件

- 用户说「调一下 prompt」「优化评分 prompt」
- 用户说「简报质量不好」「最近输出不太对」
- 用户说「这条不应该评这么高/低」
- `skills/prompt-changelog.md` 中连续 3 天有同类偏差

## 工具依赖

- 文件读取: `pipeline/prompts/scoring.py`, `processing.py`, `generation.py`
- 文件读取: `skills/prompt-changelog.md`
- 文件读取: `data/intermediate/` 下近 7 天的 scoring JSON
- 文件编辑: 修改对应 prompt 文件

## 操作步骤

### 步骤 1: 收集证据

读取最近的审核偏差记录：

```bash
cat skills/prompt-changelog.md
```

读取最近 7 天的评分数据，统计偏差模式：

```bash
ls data/intermediate/*-scoring.json | tail -7
# 逐个读取，找出被手动覆盖评分的条目
```

### 步骤 2: 分类问题

根据证据判断问题属于哪个 prompt：

```
问题类型 → 对应文件:

评分偏高/偏低     → pipeline/prompts/scoring.py
  - 某维度描述不够具体
  - 权重需要调整

分类错误          → pipeline/prompts/processing.py
  - 分类边界模糊
  - 缺少新的分类

文风/结构偏差     → pipeline/prompts/generation.py
  - 语气不对
  - 结构需要调整
  - 编辑视角不够锐利
```

### 步骤 3: 定位具体改动点

```
评分偏低的常见原因:
→ 对应维度的 5分/4分 描述没覆盖这类内容
→ 解法: 在描述里增加具体例子

评分偏高的常见原因:
→ 缺少负面案例
→ 解法: 在低分描述里增加"不应得高分"的情形

分类漂移的常见原因:
→ 分类定义边界模糊
→ 解法: 增加区分规则，如"如果同时满足 A 和 B，归为 X"

文风跑偏的常见原因:
→ context 注入不够具体
→ 解法: 在 context/style.md 增加正例和反例
```

### 步骤 4: 执行最小改动

```
原则:
1. 一次只改一个维度或一条规则
2. 改之前先复制旧版本作为注释
3. 改动应可被一句话描述
```

修改文件后，在 `skills/prompt-changelog.md` 记录：

```markdown
## YYYY-MM-DD
- 文件: scoring.py
- 改动: D1 相关性 4分描述增加"设计工具重大更新"
- 原因: Figma/Cursor 更新连续3天被评为3分
- 效果: (改后1-3天回填)
```

### 步骤 5: 验证

用最近的原始数据重新跑 pipeline 对比：

```bash
# 用昨天的数据重跑（不重新抓取）
cp data/raw/YYYY-MM-DD-*.json data/raw/$(date +%Y-%m-%d)-rerun.json
python -m pipeline.main --skip-scrape
```

对比 `data/intermediate/` 下新旧 scoring.json 的差异。

## 禁止操作

```
❌ 一次大改整个 prompt
❌ 凭感觉改权重（要有至少3天数据支撑）
❌ 删除旧版本（用注释保留）
❌ 在 prompt 里加超过3个例子（消耗 token）
```

## 关联文件

| 文件 | 用途 |
|------|------|
| `pipeline/prompts/scoring.py` | 评分 prompt（6维权重） |
| `pipeline/prompts/processing.py` | 分类 prompt |
| `pipeline/prompts/generation.py` | 生成 prompt |
| `skills/prompt-changelog.md` | 变更记录 |
| `context/style.md` | 写作风格（generation 引用）|
| `context/portrait.md` | 读者画像（scoring 引用）|
