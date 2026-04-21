---
name: context-evolution
description: Context 文件维护流程。当用户说「更新 context」「改一下读者画像」「加个新观点」「context review」「更新 style」时触发。管理 context/ 下 14 个知识体系文件的更新，确保文件间口径一致。
---

# Context 文件演进 Skill

维护 `context/` 下的知识体系文件，确保 prompt 注入的内容持续准确。

## 触发条件

- 用户说「更新 context」「改一下 portrait」
- 用户说「加个新观点到 viewpoint」
- 用户说「context review」
- 用户说「读者画像需要调整」
- 每月一次定期检查

## 工具依赖

- 文件编辑: `context/*.md`
- 文件读取: `pipeline/prompts/generation.py`（查看哪些 context 被引用）

## Context 文件地图

```
被 prompt 直接引用（改了立刻影响输出）:
  portrait.md     → scoring prompt 的读者定义
  style.md        → generation prompt 的写作规则
  viewpoint.md    → generation prompt 的编辑视角
  excellent.md    → generation prompt 的质量标准

影响分类和判断（间接影响）:
  methodology.md  → 分类维度的方法论基础
  noun.md         → 专业术语定义

产品和运营层（不注入 prompt，指导决策）:
  product.md      → 产品定义和演进路线
  source.md       → 信源管理记录
  strategy.md     → 战略目标
  restriction.md  → 限制条件
  expectations.md → 未来预期
  failure.md      → 失败原因清单
  me.md           → 个人能力和定位
  tool.md         → 工具方法列表
```

## 操作步骤

### 更新被 prompt 引用的 context

这些文件改了会**立刻影响简报质量**，需要谨慎：

#### 步骤 1: 确认影响范围

```bash
# 查看这个 context 文件被哪个 prompt 引用
grep -r "load_context" pipeline/prompts/
```

#### 步骤 2: 编辑文件

```
原则:
- 新增内容优先，谨慎删除（旧内容可能仍有参考价值）
- 保持与其他 context 文件的口径一致
- 如果改了 portrait.md 的读者定义，scoring prompt 里的描述也要同步
```

#### 步骤 3: 验证

```bash
# 改完后用今天的数据重跑，对比输出差异
python -m pipeline.main --skip-scrape
diff data/output/*-briefing.md data/output/*-briefing.md.bak
```

### 更新产品/运营层 context

这些文件不直接注入 prompt，改了不影响当天输出，但影响长期方向：

```
直接编辑即可，不需要重跑 pipeline 验证。

常见场景:
- product.md → PMF 信号有变化时
- strategy.md → 调整北极星目标时
- source.md → 信源变更时（配合 source-management skill）
- expectations.md → 行业预期变化时
```

### 口径一致性检查

每月检查一次，确保文件间不矛盾：

```
检查项:
□ portrait.md 的用户画像 = scoring.py 里的读者描述
□ style.md 的写作规则 = generation.py 里的风格约束
□ noun.md 的术语定义 = processing.py 里的分类标签
□ product.md 的 MVP 范围 = 实际 pipeline 功能
```

## 关联文件

| 文件 | 更新频率 | 影响 |
|------|---------|------|
| `context/portrait.md` | 每周 | 评分 + 生成 |
| `context/style.md` | 每月 | 生成 |
| `context/viewpoint.md` | 每月 | 生成 |
| `context/product.md` | 每月 | 方向决策 |
| `context/source.md` | 每周 | 配合信源管理 |
| `pipeline/prompts/generation.py` | — | 查看引用关系 |
