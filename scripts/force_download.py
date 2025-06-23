#!/usr/bin/env python3

import os
import sys
import time
import warnings
import urllib3
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

from huggingface_hub import hf_hub_download, repo_info
from pathlib import Path
import subprocess

def force_download_model(model_name, max_file_size_gb=5):
    """Force download with better error handling and resume capability"""
    
    print(f"🚀 Force downloading: {model_name}")
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    
    try:
        # Get repo info to see what files we need
        info = repo_info(model_name)
        files = [f.rfilename for f in info.siblings]
        
        print(f"📋 Model has {len(files)} files")
        
        # Download smaller files first (config, tokenizer, etc.)
        small_files = [f for f in files if not f.endswith('.safetensors') and not f.endswith('.bin')]
        large_files = [f for f in files if f.endswith('.safetensors') or f.endswith('.bin')]
        
        print("📥 Downloading config and tokenizer files...")
        for file in small_files:
            try:
                print(f"  • {file}")
                hf_hub_download(
                    repo_id=model_name,
                    filename=file,
                    cache_dir=cache_dir,
                    resume_download=True,
                    force_download=False
                )
            except Exception as e:
                print(f"    ⚠️ Skipping {file}: {e}")
        
        print("📥 Downloading model files...")
        for file in large_files:
            try:
                print(f"  • {file} (this may take a while...)")
                
                # Use subprocess for large files to avoid hanging
                cmd = [
                    sys.executable, "-c", f"""
import warnings
warnings.filterwarnings('ignore')
from huggingface_hub import hf_hub_download
import sys

try:
    hf_hub_download(
        repo_id='{model_name}',
        filename='{file}',
        cache_dir='{cache_dir}',
        resume_download=True,
        force_download=False
    )
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {{e}}')
    sys.exit(1)
"""
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
                
                if result.returncode == 0 and "SUCCESS" in result.stdout:
                    print(f"    ✅ Downloaded {file}")
                else:
                    print(f"    ⚠️ Issue with {file}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"    ⏰ {file} download timed out, but may have partially completed")
            except Exception as e:
                print(f"    ❌ Error downloading {file}: {e}")
        
        # Test if we can load the model
        print("🧪 Testing model loading...")
        try:
            from mlx_lm import load
            model, tokenizer = load(model_name)
            print(f"✅ Model loads successfully: {type(model).__name__}")
            del model, tokenizer
            return True
        except Exception as e:
            print(f"⚠️ Model loading test failed: {e}")
            print("💡 But files may still be downloading in background")
            return False
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def check_download_status(model_name):
    """Check what files are already downloaded"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    # Look for model directory (contains hash)
    model_dirs = [d for d in cache_dir.glob("*") if model_name.replace("/", "--") in d.name]
    
    if not model_dirs:
        print(f"❌ No cached files found for {model_name}")
        return False
    
    model_dir = model_dirs[0]
    print(f"📁 Cache directory: {model_dir}")
    
    # Check what files exist
    if (model_dir / "snapshots").exists():
        snapshot_dirs = list((model_dir / "snapshots").glob("*"))
        if snapshot_dirs:
            snapshot_dir = snapshot_dirs[0]
            files = list(snapshot_dir.glob("*"))
            print(f"📋 Found {len(files)} cached files:")
            for file in files:
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  • {file.name} ({size_mb:.1f} MB)")
            return True
    
    return False

if __name__ == "__main__":
    model_name = "mlx-community/deepseek-coder-1.3b-instruct-mlx"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            check_download_status(model_name)
            sys.exit(0)
        else:
            model_name = sys.argv[1]
    
    print("🔍 Checking current download status...")
    check_download_status(model_name)
    
    print("\n🚀 Starting force download...")
    success = force_download_model(model_name)
    
    if success:
        print("\n🎉 Download completed successfully!")
    else:
        print("\n⚠️ Download had issues but may still be usable")
        print("💡 Try running the resume script or check if the model loads in the frontend")