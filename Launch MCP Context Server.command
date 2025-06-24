#!/bin/bash

# MCP Context Server Launcher
# Standalone Model Context Protocol server following Anthropic's specification

echo "🔗 MCP Context Server"
echo "======================"

# Navigate to the MLX_LLM_Controller directory
cd "$(dirname "$0")"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for required dependencies
echo "🔍 Checking dependencies..."
python3 -c "import flask; import flask_cors; import aiohttp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    python3 -m pip install flask flask-cors aiohttp
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Dependencies OK"

# Create necessary directories
mkdir -p context_data
mkdir -p logs

echo ""
echo "🔗 Starting MCP Context Server..."
echo ""
echo "✨ Features:"
echo "   📡 Anthropic MCP specification compliant"
echo "   💾 Context database storage and retrieval"
echo "   🔌 Standalone server (configurable port)"
echo "   🗄️ Conversation and context management"
echo ""
echo "📡 Server will start on configured port (default: 8002)"
echo "📖 Check MCP_CONTEXT_README.md for usage guide"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the MCP context server
if [ -f "start_mcp_context.py" ]; then
    python3 start_mcp_context.py
else
    echo "❌ MCP Context Server files not found"
    echo "Please ensure start_mcp_context.py exists in this directory"
    read -p "Press Enter to exit..."
    exit 1
fi

# Keep terminal open
echo ""
echo "🛑 MCP Context Server stopped."
echo "Press any key to close this window..."
read -n 1