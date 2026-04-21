# 审核今日简报

执行每日审核流程，辅助人工检查。

## 第一步：运行自动检查

```bash
python .claude/skills/daily-review/scripts/review-checker.py
```

## 第二步：展示简报内容

读取今日简报并完整展示：

```bash
cat data/output/$(date +%Y-%m-%d)-briefing.md
```

## 第三步：逐项审核

根据 review-checker.py 的输出，对每个 ⚠️ 警告项给出具体的修改建议。

重点检查：
1. 头条是否是今天最重要的信息
2. 编辑视角是否足够锐利（参考 context/viewpoint.md）
3. 有没有事实性错误

## 第四步：输出审核报告

格式：
```
✅/⚠️ 头条: [结果]
✅/⚠️ 分布: [must_read N, worth_noting N]
✅/⚠️ 编辑视角: [结果]
📊 整体: 可发布 / 需修改
```
