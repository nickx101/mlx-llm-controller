#!/usr/bin/env python3
"""
Standalone MLX LLM Controller with Precision Controls
Independent AI system with optional context database routing
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import logging
import time
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from backend.mlx_controller import MLXController, GenerationParams

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MLX-STANDALONE - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RoutingConfig:
    """Configuration for context database routing"""
    context_enabled: bool = False
    context_host: str = "localhost"
    context_port: int = 8001
    timeout: int = 5

class StandaloneMLXController:
    """Standalone MLX Controller with optional context routing"""
    
    def __init__(self):
        self.mlx_controller = MLXController()
        self.routing = RoutingConfig()
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        logger.info("Standalone MLX Controller initialized")
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check with routing status"""
            return jsonify({
                "status": "healthy",
                "timestamp": time.time(),
                "model_info": self.mlx_controller.get_model_info(),
                "routing": {
                    "context_enabled": self.routing.context_enabled,
                    "context_endpoint": f"http://{self.routing.context_host}:{self.routing.context_port}" if self.routing.context_enabled else None
                }
            })
        
        @self.app.route('/models', methods=['GET'])
        def list_models():
            """List available models"""
            # Direct implementation to avoid method call issues
            common_models = [
                "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
                "mlx-community/Qwen2.5-1.5B-Instruct-4bit", 
                "mlx-community/Qwen2.5-3B-Instruct-4bit",
                "mlx-community/DeepSeek-R1-0528-Qwen3-8B-4bit",
                "mlx-community/deepseek-coder-1.3b-instruct-mlx",
                "mlx-community/deepseek-coder-6.7b-instruct-hf-4bit-mlx",
                "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
                "mlx-community/Llama-3.2-1B-Instruct-4bit",
                "mlx-community/Llama-3.2-3B-Instruct-4bit",
                "mlx-community/gemma-2-2b-it-4bit",
                "mlx-community/Phi-3.5-mini-instruct-4bit",
                "microsoft/Phi-3.5-mini-instruct"
            ]
            
            return jsonify({
                "available_models": common_models,
                "current_model": self.mlx_controller.model_name,
                "model_loaded": self.mlx_controller.model_loaded
            })
        
        @self.app.route('/models/load', methods=['POST'])
        def load_model():
            """Load model"""
            data = request.get_json()
            model_path = data.get('model_path')
            
            if not model_path:
                return jsonify({"error": "model_path is required"}), 400
            
            try:
                success = self.mlx_controller.load_model(model_path)
                return jsonify({
                    "success": success,
                    "model_path": model_path,
                    "model_info": self.mlx_controller.get_model_info()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/models/unload', methods=['POST'])
        def unload_model():
            """Unload model"""
            try:
                self.mlx_controller.unload_model()
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/generate', methods=['POST'])
        def generate_text():
            """Generate text with optional context routing"""
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "JSON data required"}), 400
            
            messages = data.get('messages', [])
            if not messages:
                return jsonify({"error": "messages is required"}), 400
            
            # Parse parameters
            params_data = data.get('parameters', {})
            params = GenerationParams(**params_data)
            
            # Check if context routing is enabled
            conversation_id = data.get('conversation_id')
            use_context = self.routing.context_enabled and conversation_id
            
            if use_context:
                # Route to context database for enhanced messages
                enhanced_messages = self._fetch_context_enhanced_messages(messages, conversation_id)
                if enhanced_messages:
                    messages = enhanced_messages
                    logger.info(f"Applied context from database for conversation {conversation_id}")
            
            try:
                start_time = time.time()
                result = self.mlx_controller.generate_text(messages, params)
                generation_time = time.time() - start_time
                
                # Store response in context database if routing enabled
                if use_context and result.get('text'):
                    self._store_context_message(conversation_id, messages[-1]['content'], result['text'])
                
                # Add metadata
                result.update({
                    "generation_time": generation_time,
                    "model_name": self.mlx_controller.model_name,
                    "parameters_used": params.__dict__,
                    "context_enhanced": use_context,
                    "conversation_id": conversation_id if use_context else None,
                    "timestamp": time.time()
                })
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Generation failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/generate/stream', methods=['POST'])
        def stream_generate():
            """Streaming generation with optional context"""
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "JSON data required"}), 400
            
            messages = data.get('messages', [])
            if not messages:
                return jsonify({"error": "messages is required"}), 400
            
            params_data = data.get('parameters', {})
            params = GenerationParams(stream=True, **params_data)
            
            # Apply context if enabled
            conversation_id = data.get('conversation_id')
            if self.routing.context_enabled and conversation_id:
                enhanced_messages = self._fetch_context_enhanced_messages(messages, conversation_id)
                if enhanced_messages:
                    messages = enhanced_messages
            
            def generate():
                try:
                    for chunk in self.mlx_controller.stream_generate_text(messages, params):
                        yield f"data: {json.dumps(chunk)}\n\n"
                except Exception as e:
                    error_chunk = {"error": str(e), "finished": True}
                    yield f"data: {json.dumps(error_chunk)}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        
        # Routing Control Endpoints
        @self.app.route('/routing/toggle', methods=['POST'])
        def toggle_routing():
            """Toggle context database routing"""
            data = request.get_json() or {}
            enabled = data.get('enabled')
            
            if enabled is not None:
                self.routing.context_enabled = enabled
            else:
                self.routing.context_enabled = not self.routing.context_enabled
            
            # Test connection if enabling
            if self.routing.context_enabled:
                if not self._test_context_connection():
                    self.routing.context_enabled = False
                    return jsonify({
                        "error": "Cannot connect to context database",
                        "context_enabled": False
                    }), 503
            
            return jsonify({
                "context_enabled": self.routing.context_enabled,
                "context_endpoint": f"http://{self.routing.context_host}:{self.routing.context_port}" if self.routing.context_enabled else None,
                "message": f"Context routing {'enabled' if self.routing.context_enabled else 'disabled'}"
            })
        
        @self.app.route('/routing/config', methods=['GET', 'POST'])
        def routing_config():
            """Get or update routing configuration"""
            if request.method == 'GET':
                return jsonify(asdict(self.routing))
            
            data = request.get_json()
            if data:
                if 'context_host' in data:
                    self.routing.context_host = data['context_host']
                if 'context_port' in data:
                    self.routing.context_port = data['context_port']
                if 'timeout' in data:
                    self.routing.timeout = data['timeout']
            
            return jsonify(asdict(self.routing))
        
        @self.app.route('/routing/status', methods=['GET'])
        def routing_status():
            """Check routing status and connection"""
            status = {
                "enabled": self.routing.context_enabled,
                "config": asdict(self.routing),
                "connection_test": None
            }
            
            if self.routing.context_enabled:
                status["connection_test"] = self._test_context_connection()
            
            return jsonify(status)
    
    def _fetch_context_enhanced_messages(self, messages: list, conversation_id: str) -> Optional[list]:
        """Fetch context-enhanced messages from context database"""
        try:
            context_url = f"http://{self.routing.context_host}:{self.routing.context_port}/context/{conversation_id}/enhance"
            response = requests.post(
                context_url,
                json={"messages": messages},
                timeout=self.routing.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('enhanced_messages', messages)
            else:
                logger.warning(f"Context enhancement failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to fetch context: {e}")
            return None
    
    def _store_context_message(self, conversation_id: str, user_message: str, assistant_message: str):
        """Store conversation in context database"""
        try:
            context_url = f"http://{self.routing.context_host}:{self.routing.context_port}/context/{conversation_id}/store"
            requests.post(
                context_url,
                json={
                    "user_message": user_message,
                    "assistant_message": assistant_message
                },
                timeout=self.routing.timeout
            )
        except Exception as e:
            logger.warning(f"Failed to store context: {e}")
    
    def _test_context_connection(self) -> bool:
        """Test connection to context database"""
        try:
            context_url = f"http://{self.routing.context_host}:{self.routing.context_port}/health"
            response = requests.get(context_url, timeout=self.routing.timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    def run(self, host='0.0.0.0', port=8000, debug=False):
        """Run the standalone MLX controller"""
        logger.info(f"Starting Standalone MLX Controller on {host}:{port}")
        logger.info("🤖 Precision AI Controls Available")
        logger.info("🔗 Context routing: disabled (use /routing/toggle to enable)")
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standalone MLX Controller with Precision Controls")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--context-host", default="localhost", help="Context database host")
    parser.add_argument("--context-port", type=int, default=8001, help="Context database port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    controller = StandaloneMLXController()
    
    # Update routing config from args
    controller.routing.context_host = args.context_host
    controller.routing.context_port = args.context_port
    
    try:
        controller.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Standalone MLX Controller shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()