#!/bin/bash

# Legal Risk Analysis Backend Startup Script

echo "🚀 Starting Legal Risk Analysis Backend"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "❗ Please edit .env and add your ANTHROPIC_API_KEY"
    exit 1
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/documents data/images data/agent_workspace

# Start the server
echo "✅ Starting FastAPI server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
python -m app.main
