#!/usr/bin/env python3

import logging
import warnings
from huggingface_hub import list_repo_files, repo_exists
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
warnings.filterwarnings("ignore", message="urllib3.*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_availability(model_name):
    """Test if a model exists and has the required files"""
    try:
        logger.info(f"Testing: {model_name}")
        
        # Check if repo exists
        if not repo_exists(model_name):
            logger.error(f"❌ Repository does not exist: {model_name}")
            return False
        
        # List files to check structure
        files = list_repo_files(model_name)
        
        required_files = ['config.json', 'tokenizer_config.json']
        model_files = [f for f in files if f.endswith(('.safetensors', '.bin', '.mlx'))]
        
        missing_files = [f for f in required_files if f not in files]
        
        if missing_files:
            logger.warning(f"⚠️  Missing files in {model_name}: {missing_files}")
        
        if not model_files:
            logger.error(f"❌ No model files found in {model_name}")
            return False
        
        logger.info(f"✅ Available: {model_name}")
        logger.info(f"   Model files: {len(model_files)} files")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking {model_name}: {e}")
        return False

def main():
    models_to_test = [
        "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
        "mlx-community/Qwen2.5-1.5B-Instruct-4bit", 
        "mlx-community/Qwen2.5-3B-Instruct-4bit",
        "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
        "mlx-community/Llama-3.2-1B-Instruct-4bit",
        "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "mlx-community/gemma-2-2b-it-4bit",
        "mlx-community/Phi-3.5-mini-instruct-4bit",
        "mlx-community/SmolLM2-1.7B-Instruct-4bit",
        "microsoft/Phi-3.5-mini-instruct"
    ]
    
    print("🔍 Testing MLX Model Availability")
    print("=" * 50)
    
    available_models = []
    unavailable_models = []
    
    for model in models_to_test:
        if test_model_availability(model):
            available_models.append(model)
        else:
            unavailable_models.append(model)
        print()
    
    print("📊 RESULTS")
    print("=" * 50)
    print(f"✅ Available models ({len(available_models)}):")
    for model in available_models:
        print(f"   • {model}")
    
    if unavailable_models:
        print(f"\n❌ Unavailable models ({len(unavailable_models)}):")
        for model in unavailable_models:
            print(f"   • {model}")
    
    print(f"\n📋 Recommended for frontend:")
    # Prioritize smaller, faster models
    recommended = [m for m in available_models if any(size in m for size in ['0.5B', '1B', '1.5B', '1.7B'])]
    for model in recommended[:5]:
        print(f"   • {model}")

if __name__ == "__main__":
    main()