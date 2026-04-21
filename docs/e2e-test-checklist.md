# 端到端测试清单（E2E）

用于整体验证 AIDESIGN 日报与长文、语音链路。设计约定见 `.claude/CLAUDE.md` 与 `docs/run-pipeline-guide.md`。

**日期约定**：下文 `{DATE}` 为 `YYYY-MM-DD`；与 `BRIEFING_DATE`、`tools/tts_paths.py` 保持一致。

---

## 1. 环境与依赖

| # | 检查项 | 说明 |
|---|--------|------|
| ☐ | Python 3.11+ | `python3 --version` |
| ☐ | 项目依赖 | 若存在 `requirements.txt` / `pyproject.toml`，已安装 |
| ☐ | `.env` | 自 `.env.example` 复制；**至少**配置有效 `MINIMAX_API_KEY` |
| ☐ | 网络 | 抓取、LLM、TTS 需能访问对应服务 |
| ☐ | 可选：`AUTOCLI_URL` | 仅在使用 autocli 抓取登录站点 / Twitter 时 |
| ☐ | 可选：通知 | `FEISHU_WEBHOOK` / `WECHAT_WEBHOOK` / `BARK_TOKEN` / `OPENCLAW_*` 按需 |

---

## 2. 目录与配置（静态）

| # | 检查项 | 说明 |
|---|--------|------|
| ☐ | `config/sources.py` | 所需信源已启用 |
| ☐ | `context/*.md` | 存在且可被 `load_context()` 读取（尤其 `style`、`viewpoint`、`expectations`） |
| ☐ | `data/` 子目录 | `raw`、`intermediate`、`output` 可写 |

---

## 3. 端到端四步（核心）

### 3.1 步骤 1～2：抓取 + 日报

| # | 动作 | 预期 |
|---|------|------|
| ☐ | `python -m tools.test_data` | 生成 `data/raw/{DATE}-test.json` |
| ☐ | `python -m pipeline.main --skip-scrape` | 使用已有 raw 跑通 LLM 链（无 raw 时先执行上一步） |
| ☐ | （可选）`./scripts/daily-briefing.sh` 或 `python -m pipeline.main` | 真实抓取时信源与网络正常 |
| ☐ | 检查 `data/intermediate/{DATE}-scoring.json` | 存在且为合法 JSON |
| ☐ | 检查 `data/intermediate/{DATE}-processing.json` | 存在且为合法 JSON |
| ☐ | 检查 `data/output/{DATE}-briefing.md` | 非空，结构符合简报模板 |

### 3.2 步骤 2 质检（可选）

| # | 动作 | 预期 |
|---|------|------|
| ☐ | 在项目根执行：`python .claude/skills/daily-review/scripts/review-checker.py` | 能正确解析 `data/`；输出头条/分布等检查项 |

### 3.3 步骤 3：单产品对话稿 `article.md`

| # | 动作 | 预期 |
|---|------|------|
| ☐ | `python -m tools.generate_article` 或 `--date {DATE}` | LLM 调用成功 |
| ☐ | `data/output/{DATE}-article.md` | 存在；对话体、围绕单条选题（与 `pipeline/article_pick.py` 一致） |

### 3.4 步骤 4：TTS（可选）

| # | 动作 | 预期 |
|---|------|------|
| ☐ | 确认 `data/output/{DATE}-article.md` 已存在 | — |
| ☐ | `BRIEFING_DATE={DATE} python3 -m tools.article_tts`（讯飞，需 `XFYUN_*`）或 `python3 -m tools.tts_dialogue --preset edge` | 默认读 `article.md`（见 `tools/tts_paths.py`）；讯飞产出 `{DATE}-dialogue-xfyun.mp3` |
| ☐ | 依赖 | `websocket-client`、`ffmpeg`；讯飞密钥或 Edge/moviepy 等按所选路径配置 |

---

## 4. 专项与回归（按需）

| # | 检查项 | 说明 |
|---|--------|------|
| ☐ | Twitter 素材与权重 | `source_channel`、`config/settings.py` 中 `TWITTER_*` 下，含 Twitter 的条目是否进入评分池并影响简报 |
| ☐ | 无第二套对话简报 | pipeline **不**生成 `*-briefing-chat.md` |
| ☐ | 命令与文档一致 | `.claude/commands/`、`.cursor/commands/briefing-article.md` 与 `docs/run-pipeline-guide.md` |
| ☐ | Product Research（可选） | 按 `specs/product-research-agent/` 手跑一条，产出在 `data/output/product-profiles/` |

---

## 5. 一次完整跑通后的产出物

| 路径 | 应有 |
|------|------|
| `data/raw/{DATE}-*.json` | 至少一条 |
| `data/intermediate/{DATE}-scoring.json` | 有 |
| `data/intermediate/{DATE}-processing.json` | 有 |
| `data/output/{DATE}-briefing.md` | 有 |
| `data/output/{DATE}-article.md` | 执行步骤 3 后 |
| `data/output/{DATE}-dialogue*.mp3` | 仅当执行步骤 4 |

---

## 6. 失败时优先排查

| 现象 | 优先查 |
|------|--------|
| No raw items | 信源、`test_data`、抓取日志 |
| LLM 返回 JSON 异常 | `data/intermediate/` 是否截断、`SCORING_POOL_SIZE` |
| API 401/403 | `.env` 中 `MINIMAX_API_KEY` |
| article 报缺 processing | 日期与 `--date` / `BRIEFING_DATE` 是否一致 |
| TTS 找不到输入 | `{DATE}-article.md` 是否存在；`BRIEFING_DATE` |
| review-checker 路径或 data 找不到 | **必须在项目根目录**执行；见脚本内 `PROJECT_ROOT` |

---

## 7. 关联文档

| 文档 | 用途 |
|------|------|
| `.claude/CLAUDE.md` | 四步流程与 Agent/Skill |
| `docs/run-pipeline-guide.md` | 命令与排错 |
| `docs/prompt-tuning-guide.md` | prompt 迭代（可选） |
