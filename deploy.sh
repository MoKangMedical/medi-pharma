#!/bin/bash
# MediPharma 一键部署脚本
# 用法: bash deploy.sh [port]

PORT=${1:-8092}
echo "💊 MediPharma v2.0 部署中..."
echo "   端口: $PORT"

cd "$(dirname "$0")"
python3 -c "import fastapi" 2>/dev/null || pip3 install fastapi uvicorn

echo "   启动 API 服务..."
python3 -m uvicorn backend.api:app --host 0.0.0.0 --port $PORT &
sleep 2

echo "✅ MediPharma 已启动: http://localhost:$PORT"
echo "   API文档: http://localhost:$PORT/docs"
echo "   健康检查: http://localhost:$PORT/health"
