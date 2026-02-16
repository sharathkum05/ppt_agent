#!/bin/bash

# Simple script to start the project on localhost

echo "🚀 Starting PPT Agent on Localhost..."
echo ""

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run: python3 -m venv venv"
    exit 1
fi

# Start backend in background
echo "🔧 Starting backend on http://localhost:8001..."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 2

# Start frontend in a new terminal (optional)
echo ""
echo "🎨 To start the frontend, open a new terminal and run:"
echo "   cd $PROJECT_DIR/ppt-agent-frontend"
echo "   npm run dev"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Backend is running!"
echo ""
echo "📍 Backend API: http://localhost:8001"
echo "📍 API Docs: http://localhost:8001/docs"
echo "📍 Health Check: http://localhost:8001/health"
echo ""
echo "🛑 To stop: pkill -f 'uvicorn.*app.main:app'"
echo "═══════════════════════════════════════════════════"




