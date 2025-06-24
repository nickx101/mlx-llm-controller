#!/usr/bin/env python3
"""
MCP Context Server - Following Anthropic's Model Context Protocol Specification
Provides context management, memory persistence, and controlled LLM integration
"""

import asyncio
import json
import logging
import sqlite3
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import argparse
import aiohttp
import hashlib
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# MCP Protocol Types following Anthropic specification
@dataclass
class MCPResource:
    """MCP Resource following protocol specification"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None

@dataclass
class MCPTool:
    """MCP Tool following protocol specification"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

@dataclass
class MCPPrompt:
    """MCP Prompt following protocol specification"""
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None

@dataclass
class AIRoutingConfig:
    """Configuration for AI controller routing"""
    ai_enabled: bool = False
    ai_host: str = "localhost"
    ai_port: int = 8000
    timeout: int = 10

class ContextDatabase:
    """SQLite database for context persistence"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens INTEGER DEFAULT 0,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                );
                
                CREATE TABLE IF NOT EXISTS context_windows (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    window_size INTEGER NOT NULL,
                    strategy TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                );
                
                CREATE TABLE IF NOT EXISTS context_injections (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_messages_conversation 
                ON messages(conversation_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_injections_conversation 
                ON context_injections(conversation_id, priority DESC);
            ''')
    
    def create_conversation(self, name: str, metadata: Dict = None) -> str:
        """Create new conversation"""
        conv_id = hashlib.md5(f"{name}_{datetime.now()}".encode()).hexdigest()[:16]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (id, name, metadata) VALUES (?, ?, ?)",
                (conv_id, name, json.dumps(metadata or {}))
            )
        return conv_id
    
    def add_message(self, conversation_id: str, role: str, content: str, tokens: int = 0):
        """Add message to conversation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, tokens) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, tokens)
            )
            # Update conversation timestamp
            conn.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )
    
    def get_conversation_history(self, conversation_id: str, limit: int = None) -> List[Dict]:
        """Get conversation history with optional limit"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT role, content, timestamp, tokens 
                FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp DESC
            """
            if limit:
                query += f" LIMIT {limit}"
            
            rows = conn.execute(query, (conversation_id,)).fetchall()
            return [dict(row) for row in reversed(rows)]
    
    def add_context_injection(self, conversation_id: str, injection_type: str, 
                            content: str, priority: int = 0) -> str:
        """Add context injection"""
        injection_id = hashlib.md5(f"{conversation_id}_{injection_type}_{datetime.now()}".encode()).hexdigest()[:16]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO context_injections (id, conversation_id, type, content, priority) VALUES (?, ?, ?, ?, ?)",
                (injection_id, conversation_id, injection_type, content, priority)
            )
        return injection_id
    
    def get_active_injections(self, conversation_id: str) -> List[Dict]:
        """Get active context injections for conversation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM context_injections WHERE conversation_id = ? AND active = 1 ORDER BY priority DESC",
                (conversation_id,)
            ).fetchall()
            return [dict(row) for row in rows]

class MCPContextServer:
    """MCP Context Server following Anthropic's specification"""
    
    def __init__(self, db_path: str, llm_port: int = 8000):
        self.db = ContextDatabase(db_path)
        self.llm_port = llm_port
        self.llm_base_url = f"http://localhost:{llm_port}"
        self.routing = AIRoutingConfig(ai_port=llm_port)
        
        # MCP Server Info
        self.server_info = {
            "name": "mcp-context-server",
            "version": "1.0.0"
        }
        
        # Initialize capabilities
        self.capabilities = {
            "resources": {},
            "tools": {},
            "prompts": {}
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - MCP-CONTEXT - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"MCP Context Server initialized")
        self.logger.info(f"Database: {db_path}")
        self.logger.info(f"LLM Port: {llm_port}")
        self.logger.info(f"🔗 Context routing: {'enabled' if self.routing.ai_enabled else 'disabled'} (use /routing/toggle to enable)")
    
    # MCP Protocol Methods
    async def handle_initialize(self, params: Dict) -> Dict:
        """Handle MCP initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                },
                "tools": {
                    "listChanged": True
                },
                "prompts": {
                    "listChanged": True
                }
            },
            "serverInfo": self.server_info
        }
    
    async def handle_resources_list(self, params: Dict = None) -> Dict:
        """List available context resources"""
        resources = []
        
        # Add conversation resources
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            conversations = conn.execute(
                "SELECT id, name, created_at FROM conversations ORDER BY updated_at DESC"
            ).fetchall()
            
            for conv in conversations:
                resources.append({
                    "uri": f"context://conversation/{conv['id']}",
                    "name": f"Conversation: {conv['name']}",
                    "description": f"Context from conversation {conv['name']} (created {conv['created_at']})",
                    "mimeType": "application/json"
                })
        
        return {"resources": resources}
    
    async def handle_resources_read(self, params: Dict) -> Dict:
        """Read context resource content"""
        uri = params.get("uri", "")
        
        if uri.startswith("context://conversation/"):
            conv_id = uri.split("/")[-1]
            history = self.db.get_conversation_history(conv_id)
            injections = self.db.get_active_injections(conv_id)
            
            content = {
                "conversation_id": conv_id,
                "message_history": history,
                "context_injections": injections,
                "total_messages": len(history),
                "active_injections": len(injections)
            }
            
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(content, indent=2)
                }]
            }
        
        return {"contents": []}
    
    async def handle_tools_list(self, params: Dict = None) -> Dict:
        """List available context management tools"""
        tools = [
            {
                "name": "create_conversation",
                "description": "Create a new conversation context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Conversation name"},
                        "metadata": {"type": "object", "description": "Optional metadata"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "add_context_injection",
                "description": "Inject context into conversation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string", "description": "Target conversation"},
                        "type": {"type": "string", "enum": ["system", "background", "instruction", "knowledge"]},
                        "content": {"type": "string", "description": "Context content"},
                        "priority": {"type": "integer", "description": "Priority (higher = more important)"}
                    },
                    "required": ["conversation_id", "type", "content"]
                }
            },
            {
                "name": "generate_with_context",
                "description": "Generate LLM response with managed context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string", "description": "Conversation context"},
                        "message": {"type": "string", "description": "User message"},
                        "window_size": {"type": "integer", "description": "Context window size", "default": 10},
                        "temperature": {"type": "number", "description": "LLM temperature", "default": 0.7}
                    },
                    "required": ["conversation_id", "message"]
                }
            },
            {
                "name": "manage_context_window",
                "description": "Configure context window for conversation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string", "description": "Target conversation"},
                        "window_size": {"type": "integer", "description": "Number of messages to keep"},
                        "strategy": {"type": "string", "enum": ["recent", "important", "semantic"], "default": "recent"}
                    },
                    "required": ["conversation_id", "window_size"]
                }
            }
        ]
        
        return {"tools": tools}
    
    async def handle_tools_call(self, params: Dict) -> Dict:
        """Execute context management tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "create_conversation":
                conv_id = self.db.create_conversation(
                    arguments["name"], 
                    arguments.get("metadata", {})
                )
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Created conversation: {conv_id}"
                    }],
                    "isError": False
                }
            
            elif tool_name == "add_context_injection":
                injection_id = self.db.add_context_injection(
                    arguments["conversation_id"],
                    arguments["type"],
                    arguments["content"],
                    arguments.get("priority", 0)
                )
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Added context injection: {injection_id}"
                    }],
                    "isError": False
                }
            
            elif tool_name == "generate_with_context":
                result = await self.generate_with_context(
                    arguments["conversation_id"],
                    arguments["message"],
                    arguments.get("window_size", 10),
                    arguments.get("temperature", 0.7)
                )
                return {
                    "content": [{
                        "type": "text",
                        "text": result
                    }],
                    "isError": False
                }
            
            elif tool_name == "manage_context_window":
                # Store window configuration
                with sqlite3.connect(self.db.db_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO context_windows (id, conversation_id, window_size, strategy) VALUES (?, ?, ?, ?)",
                        (arguments["conversation_id"], arguments["conversation_id"], arguments["window_size"], arguments.get("strategy", "recent"))
                    )
                return {
                    "content": [{
                        "type": "text", 
                        "text": f"Updated context window for conversation {arguments['conversation_id']}"
                    }],
                    "isError": False
                }
            
            else:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }],
                    "isError": True
                }
                
        except Exception as e:
            self.logger.error(f"Tool execution error: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": f"Tool execution failed: {str(e)}"
                }],
                "isError": True
            }
    
    async def generate_with_context(self, conversation_id: str, message: str, 
                                  window_size: int = 10, temperature: float = 0.7) -> str:
        """Generate LLM response with managed context"""
        # Get conversation history
        history = self.db.get_conversation_history(conversation_id, window_size)
        
        # Get active context injections
        injections = self.db.get_active_injections(conversation_id)
        
        # Build context-aware messages
        messages = []
        
        # Add context injections as system messages
        for injection in injections:
            if injection['type'] == 'system':
                messages.append({
                    "role": "system",
                    "content": injection['content']
                })
        
        # Add conversation history
        messages.extend([
            {"role": msg["role"], "content": msg["content"]} 
            for msg in history
        ])
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Send to LLM
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.llm_base_url}/generate",
                    json={
                        "messages": messages,
                        "parameters": {
                            "temperature": temperature,
                            "max_length": 1024
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        llm_response = result.get("text", "")
                        
                        # Store in database
                        self.db.add_message(conversation_id, "user", message)
                        self.db.add_message(conversation_id, "assistant", llm_response)
                        
                        return llm_response
                    else:
                        error_msg = f"LLM request failed: {response.status}"
                        self.logger.error(error_msg)
                        return error_msg
                        
        except Exception as e:
            error_msg = f"Failed to connect to LLM: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def _test_ai_connection(self) -> bool:
        """Test connection to AI controller"""
        try:
            response = requests.get(
                f"http://{self.routing.ai_host}:{self.routing.ai_port}/health",
                timeout=self.routing.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"AI connection test failed: {e}")
            return False
    
    def setup_http_api(self, port: int = 8002):
        """Setup HTTP API for configuration and routing control"""
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health', methods=['GET'])
        def health_check():
            """Health check with routing status"""
            return jsonify({
                "status": "healthy",
                "timestamp": time.time(),
                "mcp_server": "active",
                "routing": {
                    "ai_enabled": self.routing.ai_enabled,
                    "ai_endpoint": f"http://{self.routing.ai_host}:{self.routing.ai_port}" if self.routing.ai_enabled else None
                }
            })
        
        @app.route('/routing/toggle', methods=['POST'])
        def toggle_routing():
            """Toggle AI controller routing"""
            data = request.get_json() or {}
            enabled = data.get('enabled')
            
            if enabled is not None:
                self.routing.ai_enabled = enabled
            else:
                self.routing.ai_enabled = not self.routing.ai_enabled
            
            # Test connection if enabling
            if self.routing.ai_enabled:
                if not self._test_ai_connection():
                    self.routing.ai_enabled = False
                    return jsonify({
                        "error": "Cannot connect to AI controller",
                        "ai_enabled": False
                    }), 503
            
            return jsonify({
                "ai_enabled": self.routing.ai_enabled,
                "ai_endpoint": f"http://{self.routing.ai_host}:{self.routing.ai_port}" if self.routing.ai_enabled else None,
                "message": f"AI routing {'enabled' if self.routing.ai_enabled else 'disabled'}"
            })
        
        @app.route('/routing/config', methods=['GET', 'POST'])
        def routing_config():
            """Get or update routing configuration"""
            if request.method == 'GET':
                return jsonify(asdict(self.routing))
            
            data = request.get_json()
            if data:
                if 'ai_host' in data:
                    self.routing.ai_host = data['ai_host']
                if 'ai_port' in data:
                    self.routing.ai_port = data['ai_port']
                if 'timeout' in data:
                    self.routing.timeout = data['timeout']
            
            return jsonify(asdict(self.routing))
        
        @app.route('/routing/status', methods=['GET'])
        def routing_status():
            """Check routing status and connection"""
            status = {
                "enabled": self.routing.ai_enabled,
                "config": asdict(self.routing),
                "connection_test": None
            }
            
            if self.routing.ai_enabled:
                status["connection_test"] = self._test_ai_connection()
            
            return jsonify(status)
        
        # Start HTTP API server in separate thread
        def run_api():
            app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        self.logger.info(f"🌐 HTTP API started on port {port}")
        self.logger.info(f"📡 Routing endpoints: /routing/toggle, /routing/status, /routing/config")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCP Context Server")
    parser.add_argument("--db-path", default="./context_data/conversations.db", 
                       help="Database file path")
    parser.add_argument("--llm-port", type=int, default=8000,
                       help="LLM server port")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                       help="Transport method")
    parser.add_argument("--api-port", type=int, default=8002,
                       help="HTTP API server port for routing control")
    
    args = parser.parse_args()
    
    # Create context server
    server = MCPContextServer(args.db_path, args.llm_port)
    
    # Start HTTP API for routing control
    server.setup_http_api(args.api_port)
    
    if args.transport == "stdio":
        # STDIO transport for MCP clients
        import sys
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                method = request.get("method", "")
                params = request.get("params", {})
                
                # Route MCP methods
                if method == "initialize":
                    result = await server.handle_initialize(params)
                elif method == "resources/list":
                    result = await server.handle_resources_list(params)
                elif method == "resources/read":
                    result = await server.handle_resources_read(params)
                elif method == "tools/list":
                    result = await server.handle_tools_list(params)
                elif method == "tools/call":
                    result = await server.handle_tools_call(params)
                else:
                    result = {"error": f"Unknown method: {method}"}
                
                # Send response
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    else:
        print("SSE transport not implemented yet")

if __name__ == "__main__":
    asyncio.run(main())