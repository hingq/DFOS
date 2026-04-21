#!/bin/bash
# run.sh — 一键执行每日简报 pipeline
# 用法: bash run.sh
# 定时: crontab -e → 0 5 * * * cd /path/to/daily-briefing && bash run.sh >> logs/$(date +\%Y-\%m-\%d).log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "$(date '+%Y-%m-%d %H:%M:%S') — Starting daily briefing pipeline"

# 激活虚拟环境（如果有的话）
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 执行 pipeline
python -m pipeline.main

echo "$(date '+%Y-%m-%d %H:%M:%S') — Pipeline complete"
