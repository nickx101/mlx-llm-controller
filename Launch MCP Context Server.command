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

# Configuration variables
ROUTING_ENABLED="false"
AI_HOST="localhost"
AI_PORT="8000"
API_PORT="8002"
DB_PATH="./context_data/conversations.db"

echo ""
echo "🔗 MCP Context Server Configuration"
echo "====================================="
echo ""
echo "✨ Features Available:"
echo "   📡 Anthropic MCP specification compliant"
echo "   💾 Context database storage and retrieval"
echo "   🔌 Standalone server (configurable port)"
echo "   🗄️ Conversation and context management"
echo "   🔗 Optional AI controller routing"
echo ""

# Configuration menu
echo "🎛️  Configuration Options:"
echo "1. Quick Start (default settings, routing disabled)"
echo "2. Enable AI Routing (connect to MLX AI Controller)"
echo "3. Custom Configuration"
echo "4. Show Current Settings"
echo ""

read -p "Select option (1-4): " config_option

case $config_option in
    1)
        echo ""
        echo "✅ Quick Start selected - Default settings"
        echo "   📡 API Port: $API_PORT"
        echo "   💾 Database: $DB_PATH" 
        echo "   🔗 AI Routing: Disabled"
        ;;
    2)
        echo ""
        echo "🔗 AI Routing Configuration"
        echo "============================"
        ROUTING_ENABLED="true"
        
        read -p "AI Controller Host [$AI_HOST]: " input_host
        if [ ! -z "$input_host" ]; then
            AI_HOST="$input_host"
        fi
        
        read -p "AI Controller Port [$AI_PORT]: " input_port
        if [ ! -z "$input_port" ]; then
            AI_PORT="$input_port"
        fi
        
        echo ""
        echo "✅ AI Routing enabled"
        echo "   🤖 AI Endpoint: http://$AI_HOST:$AI_PORT"
        ;;
    3)
        echo ""
        echo "⚙️  Custom Configuration"
        echo "========================"
        
        read -p "Database path [$DB_PATH]: " input_db
        if [ ! -z "$input_db" ]; then
            DB_PATH="$input_db"
        fi
        
        read -p "HTTP API port [$API_PORT]: " input_api_port
        if [ ! -z "$input_api_port" ]; then
            API_PORT="$input_api_port"
        fi
        
        read -p "Enable AI routing? (y/n) [n]: " input_routing
        if [ "$input_routing" = "y" ] || [ "$input_routing" = "Y" ]; then
            ROUTING_ENABLED="true"
            
            read -p "AI Controller Host [$AI_HOST]: " input_host
            if [ ! -z "$input_host" ]; then
                AI_HOST="$input_host"
            fi
            
            read -p "AI Controller Port [$AI_PORT]: " input_port
            if [ ! -z "$input_port" ]; then
                AI_PORT="$input_port"
            fi
        fi
        
        echo ""
        echo "✅ Custom configuration set"
        ;;
    4)
        echo ""
        echo "📋 Current Settings"
        echo "=================="
        echo "   📡 API Port: $API_PORT"
        echo "   💾 Database: $DB_PATH"
        echo "   🔗 AI Routing: $ROUTING_ENABLED"
        if [ "$ROUTING_ENABLED" = "true" ]; then
            echo "   🤖 AI Endpoint: http://$AI_HOST:$AI_PORT"
        fi
        echo ""
        read -p "Continue with these settings? (y/n): " continue_choice
        if [ "$continue_choice" != "y" ] && [ "$continue_choice" != "Y" ]; then
            echo "Configuration cancelled"
            exit 0
        fi
        ;;
    *)
        echo "Invalid option. Using default settings..."
        ;;
esac

echo ""
echo "🚀 Starting MCP Context Server..."
echo "=================================="
echo "   📡 API Port: $API_PORT"
echo "   💾 Database: $DB_PATH"
echo "   🔗 AI Routing: $ROUTING_ENABLED"
if [ "$ROUTING_ENABLED" = "true" ]; then
    echo "   🤖 AI Endpoint: http://$AI_HOST:$AI_PORT"
fi
echo ""
echo "📡 HTTP API Endpoints:"
echo "   POST /routing/toggle - Toggle AI routing"
echo "   GET  /routing/status - Check routing status"
echo "   GET  /health - Server health check"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Build command arguments
ARGS="--db-path \"$DB_PATH\" --api-port $API_PORT"

# Start the MCP context server
if [ -f "start_mcp_context.py" ]; then
    if [ "$ROUTING_ENABLED" = "true" ]; then
        echo "🔗 Pre-enabling AI routing..."
        # Start server in background briefly to enable routing
        eval "python3 start_mcp_context.py $ARGS" &
        SERVER_PID=$!
        sleep 3
        
        # Enable routing
        curl -s -X POST http://localhost:$API_PORT/routing/toggle -H "Content-Type: application/json" -d "{\"enabled\": true}" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✅ AI routing enabled"
        else
            echo "⚠️  AI routing could not be enabled (AI controller may not be running)"
        fi
        
        # Kill background server and restart normally
        kill $SERVER_PID > /dev/null 2>&1
        sleep 1
    fi
    
    # Start server normally
    eval "python3 start_mcp_context.py $ARGS"
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