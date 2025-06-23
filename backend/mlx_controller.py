import logging
import time
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Generator
import threading
from dataclasses import dataclass, asdict

import urllib3
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
warnings.filterwarnings("ignore", message="urllib3.*")

import mlx.core as mx
from mlx_lm import load, generate, stream_generate
from mlx_lm.sample_utils import make_sampler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WORKER-claude-001 - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/aura/AI_CORE/logs/worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MLXControllerError(Exception):
    def __init__(self, message, context=None):
        super().__init__(message)
        self.context = context
        logger.error(f"MLXControllerError: {message}")

@dataclass
class GenerationParams:
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    max_length: int = 512
    stop_sequences: List[str] = None
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    repetition_penalty: float = 1.05
    repetition_context_size: int = 20
    min_p: float = 0.0
    stream: bool = False
    verbose: bool = True
    
    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def validate(self) -> bool:
        try:
            assert 0.0 <= self.temperature <= 2.0, "Temperature must be between 0.0 and 2.0"
            assert 0.0 <= self.top_p <= 1.0, "Top-p must be between 0.0 and 1.0"
            assert self.top_k >= 0, "Top-k must be >= 0"
            assert self.max_length > 0, "Max length must be > 0"
            assert self.repetition_penalty >= 1.0, "Repetition penalty must be >= 1.0"
            assert 0.0 <= self.min_p <= 1.0, "Min-p must be between 0.0 and 1.0"
            return True
        except AssertionError as e:
            logger.error(f"Parameter validation failed: {e}")
            return False

class CustomLogitsProcessor:
    def __init__(self, frequency_penalty: float = 0.0, presence_penalty: float = 0.0, repetition_penalty: float = 1.0):
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.repetition_penalty = repetition_penalty
        self.token_frequencies = {}
        self.used_tokens = set()
        self.context_tokens = []
    
    def __call__(self, tokens: mx.array, logits: mx.array) -> mx.array:
        if (self.frequency_penalty == 0.0 and 
            self.presence_penalty == 0.0 and 
            self.repetition_penalty == 1.0):
            return logits
        
        modified_logits = logits.copy()
        
        # Update context with new tokens
        for token_id in tokens:
            token_id_val = int(token_id)
            self.context_tokens.append(token_id_val)
            
            # Apply frequency penalty
            if self.frequency_penalty != 0.0:
                count = self.token_frequencies.get(token_id_val, 0)
                if count > 0:
                    modified_logits[token_id_val] -= self.frequency_penalty * count
            
            # Apply presence penalty
            if self.presence_penalty != 0.0 and token_id_val in self.used_tokens:
                modified_logits[token_id_val] -= self.presence_penalty
            
            # Apply repetition penalty
            if self.repetition_penalty != 1.0 and token_id_val in self.context_tokens[:-1]:
                if modified_logits[token_id_val] > 0:
                    modified_logits[token_id_val] /= self.repetition_penalty
                else:
                    modified_logits[token_id_val] *= self.repetition_penalty
            
            # Update tracking
            self.token_frequencies[token_id_val] = self.token_frequencies.get(token_id_val, 0) + 1
            self.used_tokens.add(token_id_val)
        
        # Keep context window manageable (last 50 tokens)
        if len(self.context_tokens) > 50:
            self.context_tokens = self.context_tokens[-50:]
        
        return modified_logits

class MLXController:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = None
        self.model_loaded = False
        self._generation_lock = threading.Lock()
        logger.info("MLXController initialized")
    
    def load_model(self, model_path: str, tokenizer_config: Optional[Dict] = None) -> bool:
        try:
            logger.info(f"Loading model: {model_path}")
            start_time = time.time()
            
            # Add retry logic for network issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if tokenizer_config:
                        self.model, self.tokenizer = load(model_path, tokenizer_config=tokenizer_config)
                    else:
                        self.model, self.tokenizer = load(model_path)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Load attempt {attempt + 1} failed: {e}. Retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise e
            
            self.model_name = model_path
            self.model_loaded = True
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f}s: {model_path}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "cannot find the requested files" in error_msg or "locate the file on the Hub" in error_msg:
                error_msg = f"Model '{model_path}' not found. Please check the model name or try a different model."
            elif "Connection" in error_msg or "network" in error_msg.lower():
                error_msg = f"Network error loading '{model_path}'. Please check your internet connection and try again."
            
            logger.error(f"Failed to load model {model_path}: {error_msg}")
            raise MLXControllerError(f"Model loading failed: {error_msg}")
    
    def unload_model(self):
        try:
            self.model = None
            self.tokenizer = None
            self.model_name = None
            self.model_loaded = False
            logger.info("Model unloaded successfully")
        except Exception as e:
            logger.error(f"Error during model unload: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "loaded": self.model_loaded,
            "model_name": self.model_name,
            "model_type": type(self.model).__name__ if self.model else None
        }
    
    def _prepare_prompt(self, messages: List[Dict[str, str]]) -> str:
        if not self.tokenizer:
            raise MLXControllerError("No tokenizer loaded")
        
        try:
            if hasattr(self.tokenizer, 'apply_chat_template'):
                return self.tokenizer.apply_chat_template(
                    messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
            else:
                prompt = ""
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    prompt += f"<|{role}|>{content}<|end|>\n"
                return prompt
        except Exception as e:
            logger.error(f"Error preparing prompt: {e}")
            raise MLXControllerError(f"Prompt preparation failed: {e}")
    
    def _create_sampler(self, params: GenerationParams):
        try:
            sampler_kwargs = {
                "temp": params.temperature,
                "top_p": params.top_p,
                "min_p": params.min_p,
                "min_tokens_to_keep": 1
            }
            
            # Only add top_k if it's greater than 0
            if params.top_k > 0:
                sampler_kwargs["top_k"] = params.top_k
                
            return make_sampler(**sampler_kwargs)
        except Exception as e:
            logger.error(f"Error creating sampler: {e}")
            raise MLXControllerError(f"Sampler creation failed: {e}")
    
    def generate_text(self, messages: List[Dict[str, str]], params: GenerationParams) -> Dict[str, Any]:
        if not self.model_loaded:
            raise MLXControllerError("No model loaded")
        
        if not params.validate():
            raise MLXControllerError("Invalid generation parameters")
        
        with self._generation_lock:
            try:
                logger.info(f"Starting text generation with params: {params.to_dict()}")
                start_time = time.time()
                
                prompt = self._prepare_prompt(messages)
                sampler = self._create_sampler(params)
                
                response = generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    sampler=sampler,
                    max_tokens=params.max_length,
                    verbose=params.verbose
                )
                
                generation_time = time.time() - start_time
                
                result = {
                    "text": response,
                    "prompt": prompt,
                    "generation_time": generation_time,
                    "parameters_used": params.to_dict(),
                    "model_name": self.model_name
                }
                
                logger.info(f"Text generation completed in {generation_time:.2f}s")
                return result
                
            except Exception as e:
                logger.error(f"Generation failed: {e}")
                raise MLXControllerError(f"Text generation failed: {e}")
    
    def stream_generate_text(self, messages: List[Dict[str, str]], params: GenerationParams) -> Generator[Dict[str, Any], None, None]:
        if not self.model_loaded:
            raise MLXControllerError("No model loaded")
        
        if not params.validate():
            raise MLXControllerError("Invalid generation parameters")
        
        with self._generation_lock:
            try:
                logger.info(f"Starting streaming generation with params: {params.to_dict()}")
                start_time = time.time()
                
                prompt = self._prepare_prompt(messages)
                sampler = self._create_sampler(params)
                
                token_count = 0
                full_response = ""
                
                for token in stream_generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    sampler=sampler,
                    max_tokens=params.max_length
                ):
                    token_count += 1
                    full_response += token.text
                    
                    yield {
                        "token": token.text,
                        "token_count": token_count,
                        "full_text": full_response,
                        "finished": False
                    }
                    
                    if any(stop_seq in full_response for stop_seq in params.stop_sequences):
                        logger.info(f"Generation stopped by stop sequence")
                        break
                
                generation_time = time.time() - start_time
                
                yield {
                    "token": "",
                    "token_count": token_count,
                    "full_text": full_response,
                    "finished": True,
                    "generation_time": generation_time,
                    "parameters_used": params.to_dict(),
                    "model_name": self.model_name
                }
                
                logger.info(f"Streaming generation completed in {generation_time:.2f}s, {token_count} tokens")
                
            except Exception as e:
                logger.error(f"Streaming generation failed: {e}")
                raise MLXControllerError(f"Streaming generation failed: {e}")

def process_generation_request(controller: MLXController, request_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not controller.model_loaded:
            return {"error": "No model loaded"}
        
        messages = request_data.get("messages", [])
        params_dict = request_data.get("parameters", {})
        
        params = GenerationParams(**params_dict)
        
        if params.stream:
            return {"error": "Use stream endpoint for streaming generation"}
        
        result = controller.generate_text(messages, params)
        return {"success": True, "result": result}
        
    except Exception as e:
        logger.error(f"Processing generation request failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    controller = MLXController()
    
    try:
        test_model = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
        logger.info(f"Testing MLX controller with model: {test_model}")
        
        controller.load_model(test_model)
        
        test_messages = [
            {"role": "user", "content": "What is machine learning?"}
        ]
        
        test_params = GenerationParams(
            temperature=0.7,
            max_length=100,
            top_p=0.9
        )
        
        result = controller.generate_text(test_messages, test_params)
        logger.info(f"Test generation result: {result['text'][:100]}...")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")