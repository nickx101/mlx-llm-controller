#!/usr/bin/env python3

import os
import warnings
import urllib3
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

from huggingface_hub import snapshot_download
import sys

def resume_download(model_name):
    print(f"🔄 Resuming download for: {model_name}")
    print("💡 This will continue where it left off...")
    
    try:
        snapshot_download(
            repo_id=model_name,
            cache_dir=os.path.expanduser("~/.cache/huggingface/hub"),
            resume_download=True,
            local_files_only=False,
            force_download=False,
            max_workers=4,
        )
        
        print("✅ Download completed!")
        
        # Test loading
        from mlx_lm import load
        print("🧪 Testing model loading...")
        model, tokenizer = load(model_name)
        print(f"✅ Model loads successfully: {type(model).__name__}")
        del model, tokenizer
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    else:
        # Default to the model you're downloading
        model_name = "mlx-community/deepseek-coder-1.3b-instruct-mlx"
        print(f"Using default model: {model_name}")
    
    resume_download(model_name)