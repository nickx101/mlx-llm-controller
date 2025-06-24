#!/bin/bash

# Launch Standalone Context Database
# Independent context management with optional AI routing

echo "🗄️ Standalone Context Database"
echo "==============================="

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
python3 -c "import sqlite3; import flask; import flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    python3 -m pip install flask flask-cors
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Dependencies OK"

echo ""
echo "🎛️  Standalone Context Database Options:"
echo "1. Start Context Database (recommended)"
echo "2. Configure database location"
echo "3. Configure AI routing"
echo "4. View database stats"
echo ""

read -p "Select option (1-4): " option

case $option in
    1)
        echo ""
        echo "🚀 Starting Standalone Context Database..."
        echo ""
        echo "✨ Features:"
        echo "   💾 Conversation persistence"
        echo "   🧠 Context injection management"
        echo "   🔗 Optional AI controller routing"
        echo ""
        echo "📡 Endpoints:"
        echo "   POST /conversations - Create conversations"
        echo "   POST /conversations/<id>/inject - Add context"
        echo "   POST /context/<id>/enhance - Enhance messages"
        echo "   POST /routing/toggle - Enable/disable AI routing"
        echo ""
        echo "🌐 Server: http://localhost:8001"
        echo "💾 Database: ./context_data/conversations.db"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        
        python3 standalone_context_database.py
        ;;
    2)
        echo ""
        echo "📁 Database Location Configuration"
        echo "================================="
        echo ""
        echo "Current: ./context_data/conversations.db"
        echo ""
        read -p "Enter custom database path: " db_path
        
        if [ -n "$db_path" ]; then
            # Create directory if needed
            mkdir -p "$(dirname "$db_path")"
            echo ""
            echo "🚀 Starting with custom database location..."
            python3 standalone_context_database.py --db-path "$db_path"
        else
            echo "Using default location..."
            python3 standalone_context_database.py
        fi
        ;;
    3)
        echo ""
        echo "🔧 AI Controller Routing Configuration"
        echo "====================================="
        echo ""
        echo "Current settings:"
        echo "  AI Host: localhost"
        echo "  AI Port: 8000"
        echo ""
        read -p "AI controller host [localhost]: " ai_host
        read -p "AI controller port [8000]: " ai_port
        
        ai_host=${ai_host:-localhost}
        ai_port=${ai_port:-8000}
        
        echo ""
        echo "🚀 Starting with custom AI routing config..."
        python3 standalone_context_database.py --ai-host "$ai_host" --ai-port "$ai_port"
        ;;
    4)
        echo ""
        echo "📊 Database Statistics"
        echo "====================="
        echo ""
        
        # Check if server is running
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo "✅ Context Database is running"
            echo ""
            echo "Database stats:"
            curl -s http://localhost:8001/stats | python3 -m json.tool
            
            echo ""
            echo "Health status:"
            curl -s http://localhost:8001/health | python3 -m json.tool
            
            echo ""
            echo "Conversations:"
            curl -s http://localhost:8001/conversations | python3 -m json.tool
        else
            echo "❌ Context Database not running"
            echo "   Please start it first with option 1"
        fi
        ;;
    *)
        echo "Invalid option. Starting Context Database..."
        python3 standalone_context_database.py
        ;;
esac

# Keep terminal open
echo ""
echo "🛑 Standalone Context Database stopped."
echo "Press any key to close this window..."
read -n 1