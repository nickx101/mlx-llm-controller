#!/bin/bash

# Launch Standalone MLX AI Controller
# Precision AI controls with optional context database routing

echo "🤖 Standalone MLX AI Controller"
echo "================================"

# Navigate to directory
cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import mlx; import mlx_lm; import flask; import flask_cors; import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    python3 -m pip install mlx mlx-lm flask flask-cors requests
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Dependencies OK"

# Create necessary directories
mkdir -p logs

echo ""
echo "🎛️  Standalone MLX AI Options:"
echo "1. Start AI Controller (recommended)"
echo "2. Configure context database routing"
echo "3. Test AI controller"
echo ""

read -p "Select option (1-3): " option

case $option in
    1)
        echo ""
        echo "🚀 Starting Standalone MLX AI Controller..."
        echo ""
        echo "✨ Features:"
        echo "   🎯 Precision parameter controls"
        echo "   🤖 Independent AI responses"
        echo "   🔗 Optional context database routing"
        echo ""
        echo "📡 Endpoints:"
        echo "   POST /generate - Generate text"
        echo "   POST /models/load - Load models"
        echo "   POST /routing/toggle - Enable/disable context routing"
        echo "   GET /routing/status - Check routing status"
        echo ""
        echo "🌐 Server: http://localhost:8000"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        
        python3 standalone_mlx_controller.py
        ;;
    2)
        echo ""
        echo "🔧 Context Database Routing Configuration"
        echo "========================================"
        echo ""
        echo "Current settings:"
        echo "  Context Host: localhost"
        echo "  Context Port: 8001"
        echo ""
        read -p "Context database host [localhost]: " context_host
        read -p "Context database port [8001]: " context_port
        
        context_host=${context_host:-localhost}
        context_port=${context_port:-8001}
        
        echo ""
        echo "🚀 Starting with custom routing config..."
        python3 standalone_mlx_controller.py --context-host "$context_host" --context-port "$context_port"
        ;;
    3)
        echo ""
        echo "🧪 Testing Standalone MLX AI Controller..."
        echo ""
        
        # Check if server is running
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ AI Controller is running"
            echo ""
            echo "Testing basic functionality..."
            
            # Test health
            echo "1. Health check:"
            curl -s http://localhost:8000/health | python3 -m json.tool
            
            echo ""
            echo "2. Available models:"
            curl -s http://localhost:8000/models | python3 -m json.tool
            
            echo ""
            echo "3. Routing status:"
            curl -s http://localhost:8000/routing/status | python3 -m json.tool
        else
            echo "❌ AI Controller not running"
            echo "   Please start it first with option 1"
        fi
        ;;
    *)
        echo "Invalid option. Starting AI Controller..."
        python3 standalone_mlx_controller.py
        ;;
esac

# Keep terminal open
echo ""
echo "🛑 Standalone MLX AI Controller stopped."
echo "Press any key to close this window..."
read -n 1