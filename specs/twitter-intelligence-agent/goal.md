# 目标

## 在平台中的位置

本 Agent 负责 **Twitter/X 侧采集**，产出写入 raw 或辅助文件；这些内容与 RSS、HN 等**合并为同一套简报素材**，经 `pipeline.main` 生成**唯一一份** `briefing.md`。Twitter **不**单独构成与 `briefing.md` 平行的「另一套日报正文」——**两路都是生成简报的资源**。详见 `.claude/CLAUDE.md` 与 `specs/daily-briefing-agent/background.md`。

## 交付成果

1. **最新情报清单**：`data/output/twitter/latest.md`
   - 记录当日发现的热点事实
   - 每条情报包含：日期、来源链接、核心内容、相关实体词
   - 可选：来源账号**粉丝数**（仅当本次通过 autocli 等真实抓取获得时写入，并标注快照日期）
   - 条目之间用 `---` 分隔

2. **每日归档**：每日结束时，将当日新情报归档至 `data/output/twitter/YYYY-MM-DD/latest.md`

3. **KOL清单**：`data/output/twitter/kol.md`
   - 记录已发现的关键意见领袖
   - 包含：用户名、**粉丝数**、**粉丝数快照日期**（`YYYY-MM-DD`）、认证状态、主要领域、首次发现日期、最近活跃日期
   - **汇总表按粉丝数降序排列**（无可靠数据时该列填 `—` 或 `待获取`，此类行排在表末）；粉丝数仅作传播面参考，不替代内容价值与认证层级的判断
   - 发现新KOL时追加至清单，并在维护时重排汇总表、刷新已抓取账号的粉丝数（按需）
   - 初始 KOL 列表：
     - @levelsio — AI 产品先驱，nomad list
     - @swyx — AI 开发者布道者
     - @jessica_chen — AI 产品设计专家
     - @steveschoger — UI 设计专家
     - @mike_wallace — AI UX 设计师
     - @producthunt — 每日产品发现

4. **实体词库**：从推文中提取的实体词（产品/公司/事件/模型等）用于扩展搜索

## 核心工作流

1. **收集**：使用关键词搜索最新推文
2. **挖掘**：从搜索结果中提取实体词
3. **扩展**：用实体词进行二次搜索
4. **发现**：识别潜在新KOL
5. **更新**：同步更新 `latest.md` 和 `kol.md`；更新 `kol.md` 时用 autocli **按需拉取/刷新** KOL 粉丝数，再按粉丝数重排汇总表
6. **归档**：每日归档一次