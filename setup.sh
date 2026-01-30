#!/bin/bash
# MA Grader Setup Script

set -e

echo "🛠️  MA Grader Setup"
echo "===================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Backend setup
echo "📦 Setting up Python backend..."
cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

echo "   Activating virtual environment..."
source venv/bin/activate

echo "   Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Frontend setup
echo ""
echo "📦 Setting up Electron frontend..."
cd "$PROJECT_DIR/frontend"

echo "   Installing npm dependencies..."
npm install

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run in development mode:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd $PROJECT_DIR/backend"
echo "    source venv/bin/activate"
echo "    python server.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd $PROJECT_DIR/frontend"
echo "    npm run electron:dev"
echo ""
echo "Or run the dev script:"
echo "    ./dev.sh"
