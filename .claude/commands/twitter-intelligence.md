# Twitter Intelligence Agent

执行 Twitter 情报收集工作流：

1. 读取 `specs/twitter-intelligence-agent/` 下的所有 spec 文件
2. 使用 opencli-rs 搜索以下关键词的热门推文：
   - AI design
   - product design
   - Figma
   - Claude AI
   - design tools
3. 从搜索结果中提取实体词，扩展搜索
4. 追踪初始 KOL 列表的最新动态：
   - @levelsio
   - @swyx
   - @jessica_chen
   - @steveschoger
   - @mike_wallace
   - @producthunt
5. 更新 `data/output/twitter/latest.md`
6. 更新 `data/output/twitter/kol.md`
7. 执行每日归档