#!/usr/bin/env python3
"""
Standalone Context Database Server
Independent context management system with dynamic routing to AI controllers
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
import sqlite3
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CONTEXT-DB - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AIRoutingConfig:
    """Configuration for AI controller routing"""
    ai_enabled: bool = False
    ai_host: str = "localhost"
    ai_port: int = 8000
    timeout: int = 10

class ContextDatabase:
    """SQLite-based context management"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        logger.info(f"Context database initialized: {db_path}")
    
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
        logger.info(f"Created conversation: {conv_id} ({name})")
        return conv_id
    
    def add_message(self, conversation_id: str, role: str, content: str, tokens: int = 0):
        """Add message to conversation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, tokens) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, tokens)
            )
            conn.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )
    
    def get_conversation_history(self, conversation_id: str, limit: int = None) -> List[Dict]:
        """Get conversation history"""
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
        logger.info(f"Added context injection: {injection_id}")
        return injection_id
    
    def get_active_injections(self, conversation_id: str) -> List[Dict]:
        """Get active context injections"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM context_injections WHERE conversation_id = ? AND active = 1 ORDER BY priority DESC",
                (conversation_id,)
            ).fetchall()
            return [dict(row) for row in rows]
    
    def get_conversations(self) -> List[Dict]:
        """Get all conversations"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, name, created_at, updated_at FROM conversations ORDER BY updated_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]

class StandaloneContextServer:
    """Standalone Context Database Server with AI routing"""
    
    def __init__(self, db_path: str):
        self.db = ContextDatabase(db_path)
        self.routing = AIRoutingConfig()
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        logger.info("Standalone Context Server initialized")
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check with routing status"""
            return jsonify({
                "status": "healthy",
                "timestamp": time.time(),
                "database": str(self.db.db_path),
                "routing": {
                    "ai_enabled": self.routing.ai_enabled,
                    "ai_endpoint": f"http://{self.routing.ai_host}:{self.routing.ai_port}" if self.routing.ai_enabled else None
                }
            })
        
        @self.app.route('/conversations', methods=['GET', 'POST'])
        def conversations():
            """List or create conversations"""
            if request.method == 'GET':
                convs = self.db.get_conversations()
                return jsonify({"conversations": convs})
            
            data = request.get_json()
            name = data.get('name')
            metadata = data.get('metadata', {})
            
            if not name:
                return jsonify({"error": "name is required"}), 400
            
            conv_id = self.db.create_conversation(name, metadata)
            return jsonify({
                "conversation_id": conv_id,
                "name": name,
                "metadata": metadata
            })
        
        @self.app.route('/conversations/<conversation_id>/messages', methods=['GET', 'POST'])
        def conversation_messages(conversation_id):
            """Get or add messages to conversation"""
            if request.method == 'GET':
                limit = request.args.get('limit', type=int)
                messages = self.db.get_conversation_history(conversation_id, limit)
                return jsonify({"messages": messages})
            
            data = request.get_json()
            role = data.get('role')
            content = data.get('content')
            tokens = data.get('tokens', 0)
            
            if not role or not content:
                return jsonify({"error": "role and content are required"}), 400
            
            self.db.add_message(conversation_id, role, content, tokens)
            return jsonify({"success": True})
        
        @self.app.route('/conversations/<conversation_id>/inject', methods=['POST'])
        def add_context_injection(conversation_id):
            """Add context injection"""
            data = request.get_json()
            injection_type = data.get('type', 'system')
            content = data.get('content')
            priority = data.get('priority', 0)
            
            if not content:
                return jsonify({"error": "content is required"}), 400
            
            injection_id = self.db.add_context_injection(conversation_id, injection_type, content, priority)
            return jsonify({
                "injection_id": injection_id,
                "conversation_id": conversation_id,
                "type": injection_type,
                "priority": priority
            })
        
        @self.app.route('/conversations/<conversation_id>/injections', methods=['GET'])
        def get_context_injections(conversation_id):
            """Get context injections for conversation"""
            injections = self.db.get_active_injections(conversation_id)
            return jsonify({"injections": injections})
        
        @self.app.route('/context/<conversation_id>/enhance', methods=['POST'])
        def enhance_messages(conversation_id):
            """Enhance messages with context (for AI routing)"""
            data = request.get_json()
            messages = data.get('messages', [])
            window_size = data.get('window_size', 10)
            
            # Get conversation history
            history = self.db.get_conversation_history(conversation_id, window_size)
            
            # Get active context injections
            injections = self.db.get_active_injections(conversation_id)
            
            # Build enhanced messages
            enhanced_messages = []
            
            # Add context injections as system messages
            for injection in injections:
                enhanced_messages.append({
                    "role": "system",
                    "content": injection['content']
                })
            
            # Add conversation history
            enhanced_messages.extend([
                {"role": msg["role"], "content": msg["content"]} 
                for msg in history
            ])
            
            # Add current messages
            enhanced_messages.extend(messages)
            
            return jsonify({
                "enhanced_messages": enhanced_messages,
                "context_applied": {
                    "injections_count": len(injections),
                    "history_count": len(history),
                    "total_messages": len(enhanced_messages)
                }
            })
        
        @self.app.route('/context/<conversation_id>/store', methods=['POST'])
        def store_conversation(conversation_id):
            """Store conversation messages (for AI routing)"""
            data = request.get_json()
            user_message = data.get('user_message')
            assistant_message = data.get('assistant_message')
            
            if user_message:
                self.db.add_message(conversation_id, "user", user_message)
            if assistant_message:
                self.db.add_message(conversation_id, "assistant", assistant_message)
            
            return jsonify({"success": True})
        
        # AI Routing Control
        @self.app.route('/routing/toggle', methods=['POST'])
        def toggle_ai_routing():
            """Toggle AI controller routing"""
            data = request.get_json() or {}
            enabled = data.get('enabled')
            
            if enabled is not None:
                self.routing.ai_enabled = enabled
            else:
                self.routing.ai_enabled = not self.routing.ai_enabled
            
            return jsonify({
                "ai_enabled": self.routing.ai_enabled,
                "ai_endpoint": f"http://{self.routing.ai_host}:{self.routing.ai_port}" if self.routing.ai_enabled else None,
                "message": f"AI routing {'enabled' if self.routing.ai_enabled else 'disabled'}"
            })
        
        @self.app.route('/routing/config', methods=['GET', 'POST'])
        def ai_routing_config():
            """Get or update AI routing configuration"""
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
        
        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """Get database statistics"""
            with sqlite3.connect(self.db.db_path) as conn:
                stats = {}
                stats['conversations'] = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
                stats['messages'] = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
                stats['injections'] = conn.execute("SELECT COUNT(*) FROM context_injections WHERE active = 1").fetchone()[0]
            
            return jsonify(stats)
    
    def run(self, host='0.0.0.0', port=8001, debug=False):
        """Run the standalone context server"""
        logger.info(f"Starting Standalone Context Database on {host}:{port}")
        logger.info("🗄️ Context management ready")
        logger.info("🔗 AI routing: disabled (use /routing/toggle to enable)")
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standalone Context Database Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--db-path", default="./context_data/conversations.db", help="Database file path")
    parser.add_argument("--ai-host", default="localhost", help="AI controller host")
    parser.add_argument("--ai-port", type=int, default=8000, help="AI controller port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    server = StandaloneContextServer(args.db_path)
    
    # Update routing config from args
    server.routing.ai_host = args.ai_host
    server.routing.ai_port = args.ai_port
    
    try:
        server.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Standalone Context Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()