#!/bin/bash

# Script to stop both backend and frontend servers

echo "🛑 Stopping PPT Agent Servers..."

pkill -9 -f "uvicorn.*ppt_agent" 2>/dev/null
pkill -9 -f "vite.*ppt-agent" 2>/dev/null

sleep 1

if pgrep -f "uvicorn.*ppt_agent" > /dev/null || pgrep -f "vite.*ppt-agent" > /dev/null; then
    echo "❌ Some servers are still running"
else
    echo "✅ All servers stopped successfully"
fi

