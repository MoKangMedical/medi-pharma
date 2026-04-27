#!/bin/bash
set -e

echo "========================================="
echo "  MediPharma v2.0 — AI Drug Discovery"
echo "========================================="

# 启动FastAPI后端
echo "[1/2] Starting FastAPI backend on port 8000..."
uvicorn backend.api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动Streamlit前端
echo "[2/2] Starting Streamlit frontend on port 8095..."
streamlit run app.py --server.port 8095 --server.address 0.0.0.0 --server.headless true &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "  Services started:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs:    http://localhost:8000/docs"
echo "  - Frontend:    http://localhost:8095"
echo "========================================="

# 等待子进程
wait $BACKEND_PID $FRONTEND_PID
