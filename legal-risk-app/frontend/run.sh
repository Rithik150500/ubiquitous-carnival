#!/bin/bash

# Legal Risk Analysis Frontend Startup Script

echo "🚀 Starting Legal Risk Analysis Frontend"
echo "========================================="

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Start the development server
echo "🌐 Starting Vite development server..."
echo "   Frontend: http://localhost:3000"
echo ""
npm run dev
