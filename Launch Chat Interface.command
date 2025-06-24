#!/bin/bash

# Simple Chat Interface Launcher
echo "🤖 MLX AI Chat Interface"
echo "========================="

cd "$(dirname "$0")"

# Check if MLX AI Controller is running
echo "🔍 Checking MLX AI Controller..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ MLX AI Controller is running on port 8000"
else
    echo "❌ MLX AI Controller not found on port 8000"
    echo ""
    echo "Please start MLX AI Controller first:"
    echo "   double-click 'Launch Standalone MLX AI.command'"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "🌐 Opening Chat Interface..."
echo "   Chat Interface: http://localhost:8080"
echo "   MLX AI Controller: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start simple HTTP server for chat interface
python3 -c "
import http.server
import socketserver
import webbrowser
import time
import threading

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def open_browser():
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}/chat_interface.html')

threading.Thread(target=open_browser, daemon=True).start()

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'Chat interface running on http://localhost:{PORT}')
    httpd.serve_forever()
"