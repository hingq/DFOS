#!/bin/bash
# ============================================================
# run-daily.sh — 用 Claude Code 执行每日简报生成
#
# 定时执行:
#   crontab -e
#   0 5 * * * cd /path/to/daily-briefing && bash run-daily.sh >> logs/$(date +\%Y-\%m-\%d).log 2>&1
#
# 手动执行:
#   bash run-daily.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DATE=$(date +%Y-%m-%d)
LOG_FILE="logs/${DATE}.log"

# 确保目录存在
mkdir -p logs data/raw data/intermediate data/output

echo "============================================================"
echo "  Daily Briefing — ${DATE}"
echo "  Started: $(date '+%H:%M:%S')"
echo "============================================================"

# ============================================================
# 核心: 用 claude -p 执行 daily-briefing command
# ============================================================
# claude -p 会:
# 1. 读取 .claude/CLAUDE.md 理解项目
# 2. 读取 .claude/commands/daily-briefing.md 的指令
# 3. 按步骤执行: 抓取 → pipeline → 质量检查
# 4. 输出结果

echo ""
echo "[$(date '+%H:%M:%S')] Running claude -p /daily-briefing ..."
echo ""

claude -p "执行 /daily-briefing 命令，生成今天(${DATE})的日报。完成后输出简报内容和运行摘要。" \
  --allowedTools "Bash(read),Bash(write),Read,Write,Edit" \
  2>&1 | tee -a "$LOG_FILE"

# ============================================================
# 检查产出
# ============================================================
echo ""
echo "------------------------------------------------------------"

BRIEFING_FILE="data/output/${DATE}-briefing.md"

if [ -f "$BRIEFING_FILE" ]; then
    LINES=$(wc -l < "$BRIEFING_FILE")
    CHARS=$(wc -c < "$BRIEFING_FILE")
    echo "✅ Briefing generated: ${BRIEFING_FILE}"
    echo "   ${LINES} lines, ${CHARS} chars"
    
    # 可选: 发送通知
    if [ -n "${FEISHU_WEBHOOK:-}" ]; then
        PREVIEW=$(head -c 300 "$BRIEFING_FILE" | tr '\n' ' ')
        curl -s -X POST "$FEISHU_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"📰 ${DATE} 日报已生成\\n\\n${PREVIEW}...\\n\\n请审核后发布。\"}}" \
            > /dev/null 2>&1
        echo "   📤 Notification sent"
    fi
else
    echo "❌ Briefing not found: ${BRIEFING_FILE}"
    echo "   Check log: ${LOG_FILE}"
    
    # 失败通知
    if [ -n "${FEISHU_WEBHOOK:-}" ]; then
        curl -s -X POST "$FEISHU_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"⚠️ ${DATE} 日报生成失败，请检查日志。\"}}" \
            > /dev/null 2>&1
    fi
fi

echo ""
echo "============================================================"
echo "  Finished: $(date '+%H:%M:%S')"
echo "============================================================"
