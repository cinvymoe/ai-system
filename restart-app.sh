#!/bin/bash

echo "=========================================="
echo "Restarting Application"
echo "=========================================="
echo ""

# 1. Kill existing Electron processes
echo "1. Stopping existing Electron processes..."
pkill -f "electron.*main.js" 2>/dev/null && echo "✅ Stopped Electron" || echo "⚠️  No Electron process found"
pkill -f "vite" 2>/dev/null && echo "✅ Stopped Vite" || echo "⚠️  No Vite process found"
sleep 1
echo ""

# 2. Build Electron TypeScript
echo "2. Building Electron TypeScript..."
npm run build:electron
if [ $? -eq 0 ]; then
    echo "✅ Electron build successful"
else
    echo "❌ Electron build failed"
    exit 1
fi
echo ""

# 3. Start the application
echo "3. Starting application..."
echo "   This will start both Vite dev server and Electron"
echo "   Press Ctrl+C to stop"
echo ""
npm run dev
