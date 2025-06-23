import logging
import json
import asyncio
import warnings
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

import urllib3
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
warnings.filterwarnings("ignore", message="urllib3.*")

from flask import Flask, request, jsonify, Response, stream_template
from flask_cors import CORS
import threading
import queue

from mlx_controller import MLXController, GenerationParams, process_generation_request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - API-SERVER - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/aura/AI_CORE/logs/api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

controller = MLXController()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_info": controller.get_model_info()
    })

@app.route('/models', methods=['GET'])
def list_models():
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
        "current_model": controller.model_name,
        "model_loaded": controller.model_loaded
    })

@app.route('/models/load', methods=['POST'])
def load_model():
    try:
        data = request.get_json()
        model_path = data.get('model_path')
        tokenizer_config = data.get('tokenizer_config')
        
        if not model_path:
            return jsonify({"error": "model_path is required"}), 400
        
        logger.info(f"Loading model: {model_path}")
        
        success = controller.load_model(model_path, tokenizer_config)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Model {model_path} loaded successfully",
                "model_info": controller.get_model_info()
            })
        else:
            return jsonify({"error": "Failed to load model"}), 500
            
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/models/unload', methods=['POST'])
def unload_model():
    try:
        controller.unload_model()
        return jsonify({
            "success": True,
            "message": "Model unloaded successfully"
        })
    except Exception as e:
        logger.error(f"Error unloading model: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_text():
    try:
        data = request.get_json()
        
        if not controller.model_loaded:
            return jsonify({"error": "No model loaded"}), 400
        
        messages = data.get('messages', [])
        if not messages:
            return jsonify({"error": "messages is required"}), 400
        
        params_data = data.get('parameters', {})
        
        try:
            params = GenerationParams(**params_data)
        except TypeError as e:
            return jsonify({"error": f"Invalid parameters: {e}"}), 400
        
        if not params.validate():
            return jsonify({"error": "Parameter validation failed"}), 400
        
        result = controller.generate_text(messages, params)
        
        return jsonify({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error in generate_text: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate/stream', methods=['POST'])
def stream_generate_text():
    try:
        data = request.get_json()
        
        if not controller.model_loaded:
            return jsonify({"error": "No model loaded"}), 400
        
        messages = data.get('messages', [])
        if not messages:
            return jsonify({"error": "messages is required"}), 400
        
        params_data = data.get('parameters', {})
        params_data['stream'] = True
        
        try:
            params = GenerationParams(**params_data)
        except TypeError as e:
            return jsonify({"error": f"Invalid parameters: {e}"}), 400
        
        if not params.validate():
            return jsonify({"error": "Parameter validation failed"}), 400
        
        def generate():
            try:
                for chunk in controller.stream_generate_text(messages, params):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                error_chunk = {"error": str(e), "finished": True}
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return Response(generate(), content_type='text/event-stream')
        
    except Exception as e:
        logger.error(f"Error in stream_generate_text: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/parameters/validate', methods=['POST'])
def validate_parameters():
    try:
        data = request.get_json()
        params_data = data.get('parameters', {})
        
        try:
            params = GenerationParams(**params_data)
            is_valid = params.validate()
            
            return jsonify({
                "valid": is_valid,
                "parameters": params.to_dict()
            })
            
        except TypeError as e:
            return jsonify({
                "valid": False,
                "error": f"Invalid parameter types: {e}"
            }), 400
            
    except Exception as e:
        logger.error(f"Error validating parameters: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/parameters/defaults', methods=['GET'])
def get_default_parameters():
    defaults = GenerationParams()
    return jsonify({
        "default_parameters": defaults.to_dict(),
        "parameter_info": {
            "temperature": {
                "type": "float",
                "range": [0.0, 2.0],
                "description": "Controls randomness in generation. Higher values = more random"
            },
            "top_p": {
                "type": "float", 
                "range": [0.0, 1.0],
                "description": "Nucleus sampling threshold. Lower values = more focused"
            },
            "top_k": {
                "type": "int",
                "range": [0, 1000],
                "description": "Limit to top K tokens. 0 = disabled"
            },
            "max_length": {
                "type": "int",
                "range": [1, 4096],
                "description": "Maximum tokens to generate"
            },
            "stop_sequences": {
                "type": "array",
                "description": "List of strings that stop generation"
            },
            "frequency_penalty": {
                "type": "float",
                "range": [0.0, 2.0],
                "description": "Penalize tokens based on frequency"
            },
            "presence_penalty": {
                "type": "float",
                "range": [0.0, 2.0], 
                "description": "Penalize tokens that have appeared"
            },
            "repetition_penalty": {
                "type": "float",
                "range": [1.0, 2.0],
                "description": "Penalize repetitive tokens"
            }
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

def run_server(host='127.0.0.1', port=8000, debug=False):
    logger.info(f"Starting MLX API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MLX API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    try:
        run_server(args.host, args.port, args.debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")