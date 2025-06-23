#!/usr/bin/env python3

import logging
import time
import sys
import signal
import os
from pathlib import Path
from typing import Optional

import mlx.core as mx
from mlx_lm import load
from huggingface_hub import snapshot_download
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MODEL-DOWNLOADER - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/aura/AI_CORE/logs/model_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelDownloader:
    def __init__(self):
        self.download_interrupted = False
        self.current_process = None
        
    def signal_handler(self, signum, frame):
        logger.info("Download interrupted by user")
        self.download_interrupted = True
        
    def download_with_retry(self, model_name: str, max_retries: int = 3, timeout: int = 1800) -> bool:
        signal.signal(signal.SIGINT, self.signal_handler)
        
        for attempt in range(max_retries):
            if self.download_interrupted:
                logger.info("Download cancelled by user")
                return False
                
            try:
                logger.info(f"Download attempt {attempt + 1}/{max_retries} for {model_name}")
                start_time = time.time()
                
                success = self._download_model_with_timeout(model_name, timeout)
                
                if success:
                    download_time = time.time() - start_time
                    logger.info(f"Model {model_name} downloaded successfully in {download_time:.2f}s")
                    return True
                else:
                    logger.warning(f"Download attempt {attempt + 1} failed or timed out")
                    
            except Exception as e:
                logger.error(f"Download attempt {attempt + 1} failed with error: {e}")
                
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        logger.error(f"Failed to download {model_name} after {max_retries} attempts")
        return False
    
    def _download_model_with_timeout(self, model_name: str, timeout: int) -> bool:
        try:
            logger.info(f"Starting download of {model_name}")
            
            if "huggingface.co" in model_name or "/" in model_name:
                logger.info("Downloading via Hugging Face Hub...")
                logger.info("⏳ This may take several minutes for large models...")
                logger.info("💡 Download will resume automatically if interrupted")
                
                # Use longer timeout and force resume
                snapshot_download(
                    repo_id=model_name,
                    cache_dir=os.path.expanduser("~/.cache/huggingface/hub"),
                    resume_download=True,
                    local_files_only=False,
                    force_download=False,  # Don't re-download existing files
                    max_workers=4,  # Parallel downloads
                )
                
                logger.info("✅ Download completed! Testing model loading...")
                model, tokenizer = load(model_name)
                logger.info(f"Model loaded successfully: {type(model).__name__}")
                
                del model, tokenizer
                return True
                
        except Exception as e:
            logger.error(f"Download failed: {e}")
            # Check if it's a partial download that we can work with
            try:
                logger.info("🔄 Attempting to load partially downloaded model...")
                model, tokenizer = load(model_name)
                logger.info("✅ Partial download is usable!")
                del model, tokenizer
                return True
            except:
                logger.error("❌ Partial download not usable")
                return False
    
    def download_deepseek_models(self):
        mlx_deepseek_models = [
            "mlx-community/deepseek-coder-1.3b-instruct-mlx",
            "mlx-community/DeepSeek-R1-0528-Qwen3-8B-4bit",
            "mlx-community/deepseek-coder-6.7b-instruct-hf-4bit-mlx"
        ]
        
        all_models = mlx_deepseek_models + [
            "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
            "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
            "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
        ]
        
        logger.info(f"Starting download of {len(all_models)} models...")
        
        successful_downloads = []
        failed_downloads = []
        
        for i, model in enumerate(all_models, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Downloading model {i}/{len(all_models)}: {model}")
            logger.info(f"{'='*60}")
            
            if self.download_interrupted:
                logger.info("Download process interrupted by user")
                break
                
            try:
                success = self.download_with_retry(model, max_retries=2, timeout=1200)
                
                if success:
                    successful_downloads.append(model)
                    logger.info(f"✅ Successfully downloaded: {model}")
                else:
                    failed_downloads.append(model)
                    logger.error(f"❌ Failed to download: {model}")
                    
            except KeyboardInterrupt:
                logger.info("Download interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Error downloading {model}: {e}")
                failed_downloads.append(model)
        
        logger.info(f"\n{'='*60}")
        logger.info("DOWNLOAD SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Successful downloads ({len(successful_downloads)}):")
        for model in successful_downloads:
            logger.info(f"  ✅ {model}")
            
        if failed_downloads:
            logger.info(f"\nFailed downloads ({len(failed_downloads)}):")
            for model in failed_downloads:
                logger.info(f"  ❌ {model}")
        
        return successful_downloads, failed_downloads
    
    def test_model_loading(self, model_name: str) -> bool:
        try:
            logger.info(f"Testing model loading: {model_name}")
            start_time = time.time()
            
            model, tokenizer = load(model_name)
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f}s")
            logger.info(f"Model type: {type(model).__name__}")
            logger.info(f"Tokenizer type: {type(tokenizer).__name__}")
            
            test_messages = [{"role": "user", "content": "Hello, how are you?"}]
            
            if hasattr(tokenizer, 'apply_chat_template'):
                prompt = tokenizer.apply_chat_template(test_messages, tokenize=False, add_generation_prompt=True)
                logger.info(f"Chat template test successful")
            else:
                logger.info("No chat template available")
            
            del model, tokenizer
            logger.info("Model test completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model loading test failed: {e}")
            return False

def main():
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        downloader = ModelDownloader()
        
        if model_name == "deepseek":
            logger.info("Starting DeepSeek models download...")
            successful, failed = downloader.download_deepseek_models()
            
            if successful:
                logger.info(f"\nTesting first successful model: {successful[0]}")
                downloader.test_model_loading(successful[0])
        else:
            logger.info(f"Downloading single model: {model_name}")
            success = downloader.download_with_retry(model_name)
            
            if success:
                downloader.test_model_loading(model_name)
    else:
        print("Usage: python3 download_model.py <model_name_or_'deepseek'>")
        print("Examples:")
        print("  python3 download_model.py deepseek")
        print("  python3 download_model.py mlx-community/Qwen2.5-1.5B-Instruct-4bit")

if __name__ == "__main__":
    main()