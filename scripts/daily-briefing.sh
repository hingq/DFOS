#!/usr/bin/env bash
# 日报主 pipeline 编排入口（Twitter 情报需先写入 raw，见文档）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"

echo "[orchestrate] 提示：Twitter/X 素材请先通过 Twitter Intelligence / autocli 写入 data/raw/，再运行本脚本。"
echo "[orchestrate] 执行: python3 -m pipeline.main $*"
exec python3 -m pipeline.main "$@"
