#!/bin/bash

# MLX LLM Frontend Controller Launcher
# Double-click this file to start the interface

echo "🧠 MLX LLM Frontend Controller"
echo "================================"

# Change to the AI_CORE directory
cd "$(dirname "$0")"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check for required dependencies
echo "🔍 Checking dependencies..."

python3 -c "import mlx; import mlx_lm; import flask; import flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    python3 -m pip install mlx mlx-lm flask flask-cors huggingface_hub requests
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Dependencies OK"

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if any models are available
echo "🤖 Checking for downloaded models..."
if [ ! -d "$HOME/.cache/huggingface/hub" ] || [ -z "$(ls -A $HOME/.cache/huggingface/hub 2>/dev/null)" ]; then
    echo "⚠️  No models found. Would you like to download a model now?"
    echo "1) Download Qwen 0.5B (recommended - ~300MB, fastest)"
    echo "2) Download DeepSeek Coder 1.3B (~1.5GB, coding focused)"
    echo "3) Skip and start anyway (use online models)"
    read -p "Choose (1-3): " choice
    
    case $choice in
        1)
            echo "📥 Downloading Qwen 0.5B model (fastest)..."
            python3 scripts/download_model.py "mlx-community/Qwen2.5-0.5B-Instruct-4bit"
            ;;
        2)
            echo "📥 Downloading DeepSeek Coder 1.3B model..."
            python3 scripts/download_model.py "mlx-community/deepseek-coder-1.3b-instruct-mlx"
            ;;
        3)
            echo "⏭️  Skipping model download"
            ;;
        *)
            echo "⏭️  Invalid choice, skipping download"
            ;;
    esac
fi

echo ""
echo "🚀 Starting MLX Frontend Controller..."
echo "================================"
echo ""
echo "🌐 The interface will open in your browser"
echo "📡 API Server: http://127.0.0.1:8000"
echo "🖥️  Frontend: http://127.0.0.1:3000"
echo ""
echo "🛑 Press Ctrl+C to stop the servers"
echo ""

# Start the application
python3 start_mlx_frontend.py

# Keep terminal open on exit
echo ""
echo "🛑 MLX Frontend stopped"
read -p "Press Enter to close this window..."