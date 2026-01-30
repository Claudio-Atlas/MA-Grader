#!/bin/bash
# MA Grader Development Script
# Runs both backend and frontend

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "🚀 Starting MA Grader in development mode..."
echo ""

# Start backend
echo "📡 Starting Python backend..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
python server.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start frontend
echo "🖥️  Starting Electron frontend..."
cd "$PROJECT_DIR/frontend"
npm run electron:dev &
FRONTEND_PID=$!

echo ""
echo "✅ MA Grader running!"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop."
echo ""

# Wait for processes
wait
