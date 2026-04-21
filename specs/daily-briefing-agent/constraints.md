# Constraints

## 素材约束（简报资源池）

- **Twitter 与「其他爬取」共同构成**当日简报素材；合流后经**同一** pipeline 生成**一份** `briefing.md`。  
- 执行顺序上通常需先完成 Twitter 采集再跑主流程（或按项目编排并行写入 raw），但**语义上**二者均为简报供稿，**不是**「Twitter 单独出一份内容 + 爬虫再出一份简报」。  
- `data/output/twitter/` 下文件为辅助与溯源，见 `twitter-intelligence-agent` spec。

## 评分约束
- 6维加权评分，维度和权重定义在 `pipeline/prompts/scoring.py`
- must_read 最多 3 条，worth_noting 最多 6 条，tool_radar 最多 3 条
- score < 2.0 直接丢弃

## 内容约束
- 不用"震惊""重磅""颠覆"等营销词
- 不复制粘贴原文，用自己的话组织
- 每条正文控制在 80-120 字
- 编辑视角必须有产品判断，不能只复述事实

## 关键词约束
- 预过滤使用 `config/keywords.py`（三层匹配：精确/短语/组合）
- 黑名单使用 `config/blacklist.py`（硬黑名单直接丢弃）

## 运行约束
- 不修改 prompt 文件
- 不修改 config 文件
- 所有产出写入 data/ 目录
- 中间结果保存到 data/intermediate/
