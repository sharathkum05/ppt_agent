#!/bin/bash

# Script to start both backend and frontend servers

echo "🚀 Starting PPT Agent Servers..."
echo ""

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Stop any existing servers
echo "🛑 Stopping existing servers..."
pkill -9 -f "uvicorn.*ppt_agent" 2>/dev/null
pkill -9 -f "vite.*ppt-agent" 2>/dev/null
sleep 2

# Build frontend
echo "📦 Building frontend..."
cd "$PROJECT_DIR/ppt-agent-frontend"
npm run build > /tmp/ppt_agent_build.log 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed. Check /tmp/ppt_agent_build.log"
    exit 1
fi
echo "✅ Frontend built successfully"

# Start backend
echo "🔧 Starting FastAPI backend on port 8001..."
cd "$PROJECT_DIR"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload > /tmp/ppt_agent_server.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/ppt_agent_server.pid

# Wait for backend to start
sleep 3
if curl -s http://127.0.0.1:8001/health > /dev/null; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check /tmp/ppt_agent_server.log"
    exit 1
fi

# Start frontend dev server (optional)
read -p "Start frontend dev server on port 5173? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎨 Starting frontend dev server on port 5173..."
    cd "$PROJECT_DIR/ppt-agent-frontend"
    npm run dev > /tmp/ppt_agent_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/ppt_agent_frontend.pid
    sleep 3
    echo "✅ Frontend dev server started (PID: $FRONTEND_PID)"
    echo "   Frontend: http://localhost:5173"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Servers started successfully!"
echo ""
echo "📍 Backend API: http://localhost:8001"
echo "📍 Backend Docs: http://localhost:8001/docs"
echo "📍 Frontend (served by backend): http://localhost:8001"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "📍 Frontend Dev Server: http://localhost:5173"
fi
echo ""
echo "📝 Logs:"
echo "   Backend: /tmp/ppt_agent_server.log"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   Frontend: /tmp/ppt_agent_frontend.log"
fi
echo ""
echo "🛑 To stop servers:"
echo "   pkill -9 -f 'uvicorn.*ppt_agent'"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   pkill -9 -f 'vite.*ppt-agent'"
fi
echo "═══════════════════════════════════════════════════"

