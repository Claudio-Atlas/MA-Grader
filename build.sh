#!/bin/bash
# MA Grader Build Script
# Creates distributable packages for Mac and Windows

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🏗️  Building MA Grader"
echo "======================"
echo ""

# Step 1: Build Python backend executable
echo "📦 Building Python backend executable..."
cd "$PROJECT_DIR/backend"

source venv/bin/activate

# Install pyinstaller if needed
pip install pyinstaller --quiet

# Build the executable
pyinstaller server.spec --clean --noconfirm

echo "   ✅ Backend executable built: dist/ma-grader-server"

# Step 2: Build Electron app
echo ""
echo "📦 Building Electron app..."
cd "$PROJECT_DIR/frontend"

# Build React app
npm run build

# Copy the built backend executable to resources
mkdir -p extraResources/backend/dist
cp -r "$PROJECT_DIR/backend/dist/ma-grader-server" extraResources/backend/dist/ 2>/dev/null || true
cp -r "$PROJECT_DIR/backend/dist/ma-grader-server.exe" extraResources/backend/dist/ 2>/dev/null || true

# Copy backend data files
cp -r "$PROJECT_DIR/backend/templates" extraResources/backend/
cp -r "$PROJECT_DIR/backend/feedback" extraResources/backend/

# Build Electron distributable
npm run electron:build

echo ""
echo "✅ Build complete!"
echo ""
echo "Distributable packages are in: $PROJECT_DIR/frontend/dist-electron/"
