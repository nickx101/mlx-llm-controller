#!/bin/bash

# MLX LLM Controller - Universal Launcher
# One launcher for all MLX functionality

echo "🚀 MLX LLM Controller - Universal Launcher"
echo "=========================================="

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
python3 -c "import mlx; import mlx_lm; import flask; import flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    python3 -m pip install mlx mlx-lm flask flask-cors huggingface_hub requests aiohttp
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Dependencies OK"

# Create necessary directories
mkdir -p logs
mkdir -p context_data

# Show options
echo ""
echo "🎛️  MLX LLM Controller Options:"
echo "1. Standalone MLX AI Controller (recommended)"
echo "2. Standalone Context Database"
echo "3. Original MLX Frontend"
echo "4. GPU Optimization"
echo "5. Run Tests"
echo ""

read -p "Select option (1-5): " option

case $option in
    1)
        echo ""
        echo "🤖 Starting Standalone MLX AI Controller..."
        echo ""
        echo "✨ Features:"
        echo "   🎯 Precision parameter controls"
        echo "   🤖 Independent AI responses (port 8000)"
        echo "   🔗 Optional context database routing"
        echo ""
        echo "📡 Key Endpoints:"
        echo "   POST /generate - Generate text"
        echo "   POST /routing/toggle - Enable/disable context routing"
        echo "   GET /routing/status - Check routing status"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        
        if [ -f "standalone_mlx_controller.py" ]; then
            python3 standalone_mlx_controller.py
        else
            echo "❌ Standalone MLX controller not found, using original..."
            python3 start_mlx_frontend.py
        fi
        ;;
    2)
        echo ""
        echo "🗄️ Starting Standalone Context Database..."
        echo ""
        echo "✨ Features:"
        echo "   💾 Conversation persistence (port 8001)"
        echo "   🧠 Context injection management"
        echo "   🔗 Optional AI controller routing"
        echo ""
        echo "📡 Key Endpoints:"
        echo "   POST /conversations - Create conversations"
        echo "   POST /conversations/<id>/inject - Add context"
        echo "   POST /routing/toggle - Enable/disable AI routing"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        
        if [ -f "standalone_context_database.py" ]; then
            python3 standalone_context_database.py
        else
            echo "❌ Standalone context database not found"
        fi
        ;;
    3)
        echo ""
        echo "🌐 Starting Original MLX Frontend..."
        echo "   Web Interface: http://localhost:3000"
        echo "   API Server: http://localhost:8000"
        echo ""
        
        # Check for models
        if [ ! -d "$HOME/.cache/huggingface/hub" ] || [ -z "$(ls -A $HOME/.cache/huggingface/hub 2>/dev/null)" ]; then
            echo "⚠️  No models found. Would you like to download a model?"
            echo "1) Download Qwen 0.5B (recommended - ~300MB)"
            echo "2) Download DeepSeek Coder 1.3B (~1.5GB)"
            echo "3) Skip and start anyway"
            read -p "Choose (1-3): " choice
            
            case $choice in
                1)
                    echo "📥 Downloading Qwen 0.5B model..."
                    python3 scripts/download_model.py "mlx-community/Qwen2.5-0.5B-Instruct-4bit"
                    ;;
                2)
                    echo "📥 Downloading DeepSeek Coder 1.3B model..."
                    python3 scripts/download_model.py "mlx-community/deepseek-coder-1.3b-instruct-mlx"
                    ;;
                3)
                    echo "⏭️  Skipping model download"
                    ;;
            esac
        fi
        
        python3 start_mlx_frontend.py
        ;;
    3)
        echo ""
        echo "🔗 Starting MCP Context Server..."
        echo "   Standalone context management"
        echo "   Follows Anthropic's MCP specification"
        echo ""
        
        if [ -f "start_mcp_context.py" ]; then
            python3 start_mcp_context.py
        else
            echo "❌ MCP Context Server files not found"
        fi
        ;;
    4)
        echo ""
        echo "⚡ Running GPU Optimization..."
        echo "   27.5GB GPU memory dedication"
        echo "   Metal Performance optimization"
        echo ""
        
        if [ -f "scripts/optimize_mlx_gpu.py" ]; then
            python3 scripts/optimize_mlx_gpu.py
        else
            echo "❌ GPU optimization script not found"
        fi
        ;;
    5)
        echo ""
        echo "🧪 Running Tests..."
        echo ""
        echo "Available tests:"
        echo "1. Standalone Systems Routing Test"
        echo "2. System Test" 
        echo "3. API Test"
        echo ""
        
        read -p "Select test (1-3): " test_choice
        
        case $test_choice in
            1)
                if [ -f "test_standalone_routing.py" ]; then
                    echo "Testing Standalone Systems with Dynamic Routing..."
                    python3 test_standalone_routing.py
                else
                    echo "❌ Standalone routing test not found"
                fi
                ;;
            2)
                if [ -f "test_system.py" ]; then
                    echo "Testing system functionality..."
                    python3 test_system.py
                else
                    echo "❌ System test not found"
                fi
                ;;
            3)
                if [ -f "test_api.py" ]; then
                    echo "Testing API functionality..."
                    python3 test_api.py
                else
                    echo "❌ API test not found"
                fi
                ;;
            *)
                echo "Invalid test selection"
                ;;
        esac
        ;;
    *)
        echo "Invalid option. Starting Standalone MLX AI (default)..."
        if [ -f "standalone_mlx_controller.py" ]; then
            python3 standalone_mlx_controller.py
        else
            python3 start_mlx_frontend.py
        fi
        ;;
esac

# Keep terminal open
echo ""
echo "🛑 MLX Controller stopped."
echo "Press any key to close this window..."
read -n 1