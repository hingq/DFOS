# AI + 设计行业日报 Pipeline

自动追踪 AI + 设计行业资讯，每天生成简报。

## 架构概览

```
Playwright 抓取 → 关键词预过滤 → LLM 评分 → LLM 分类 → LLM 生成简报 → 人工审核 → 发布
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env 填入 MINIMAX_API_KEY（MiniMax 开放平台；走 Anthropic 兼容网关）

# 3. 运行完整 pipeline
python -m pipeline.main

# 4. 手动添加内容
python -m tools.add "标题" "https://url" "推荐理由"
```

## 目录结构

```
daily-briefing/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── run.sh                        # 一键执行脚本
│
├── config/                       # 配置文件
│   ├── settings.py               # 全局配置（API key、模型选择）
│   ├── sources.py                # 信源清单
│   ├── keywords.py               # 关键词白名单
│   └── blacklist.py              # 关键词黑名单
│
├── context/                      # 你的知识体系（prompt 注入用）
│   ├── strategy.md
│   ├── style.md
│   ├── portrait.md
│   ├── me.md
│   ├── restriction.md
│   ├── methodology.md
│   ├── excellent.md
│   ├── tool.md
│   ├── noun.md
│   ├── failure.md
│   ├── viewpoint.md
│   └── expectations.md
│
├── scraper/                      # 数据采集
│   ├── __init__.py
│   ├── base.py                   # 抓取基类
│   ├── autocli.py                # Autocli 抓取
│   ├── rss.py                    # RSS 通用抓取
│   └── manual.py                 # 手动输入合并
│
├── pipeline/                     # LLM 处理流水线
│   ├── __init__.py
│   ├── main.py                   # 主流程
│   ├── prefilter.py              # 关键词预过滤
│   ├── prompts/                  # Prompt 模板（核心资产）
│   │   ├── __init__.py
│   │   ├── scoring.py            # Step 1: 评分
│   │   ├── processing.py         # Step 2: 分类 + 实体提取
│   │   └── generation.py         # Step 3: 生成简报
│   ├── llm.py                    # LLM 调用封装
│   └── notify.py                 # 完成通知
│
├── tools/                        # 工具脚本
│   ├── __init__.py
│   └── add.py                    # 手动添加条目
│
├── data/                         # 数据目录（gitignore）
│   ├── raw/                      # 每日原始抓取
│   ├── manual/                   # 手动输入
│   ├── intermediate/             # 中间处理结果
│   └── output/                   # 最终简报
│
├── logs/                         # 运行日志
│
└── .github/workflows/
    └── daily-briefing.yml        # GitHub Actions 定时任务
```

## 定时执行

- GitHub Actions: UTC 21:00 (北京时间 05:00) 自动执行
- 本地 cron: `0 5 * * * cd /path/to/daily-briefing && bash run.sh`

## Pipeline 阶段

1. **抓取** → Playwright + RSS，输出统一 JSON
2. **预过滤** → 关键词黑白名单，减少 LLM 调用量
3. **评分** → 6维加权评分（1-5分），漏斗分层
4. **分类** → 打标 + 实体提取 + 影响判断
5. **生成** → 按模板生成可发布的简报 Markdown
6. **通知** → 推送到飞书/企业微信，等待人工审核
