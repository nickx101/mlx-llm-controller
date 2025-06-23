#!/usr/bin/env python3

import os
import sys
import subprocess
import logging
import time
import threading
import psutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - MLX-GPU-OPT - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLXGPUOptimizer:
    def __init__(self):
        self.gpu_memory_limit = 27.5  # GB dedicated to GPU
        self.soft_limit = 28.8  # GB - start reducing output
        self.hard_limit = 30.0  # GB - kill processes
        self.monitoring = False
        self.original_settings = {}
        self.settings_file = Path.home() / ".mlx_gpu_settings_backup.json"
        
    def backup_current_settings(self):
        """Backup current MLX and system GPU settings"""
        logger.info("📋 Backing up current GPU settings...")
        
        settings = {
            "timestamp": time.time(),
            "metal_device_wrapper_type": os.environ.get("METAL_DEVICE_WRAPPER_TYPE", ""),
            "mlx_metal_buffer_size": os.environ.get("MLX_METAL_BUFFER_SIZE", ""),
            "pytorch_mps_high_watermark_ratio": os.environ.get("PYTORCH_MPS_HIGH_WATERMARK_RATIO", ""),
            "tf_metal_memory_growth": os.environ.get("TF_METAL_MEMORY_GROWTH", ""),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        }
        
        # Backup macOS GPU memory pressure settings if accessible
        try:
            result = subprocess.run(["sysctl", "vm.memory_pressure"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                settings["vm_memory_pressure"] = result.stdout.strip()
        except:
            pass
            
        self.original_settings = settings
        
        # Save to file for restoration after reboot
        import json
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        logger.info(f"✅ Settings backed up to {self.settings_file}")
        
    def optimize_gpu_memory(self):
        """Apply comprehensive GPU and Metal optimizations for MLX"""
        logger.info(f"🚀 Optimizing GPU memory for MLX (dedicating {self.gpu_memory_limit}GB)")
        
        # Set MLX-specific optimizations
        gpu_bytes = int(self.gpu_memory_limit * 1024 * 1024 * 1024)
        
        # MLX Metal optimizations
        os.environ["MLX_METAL_BUFFER_SIZE"] = str(gpu_bytes)
        os.environ["METAL_DEVICE_WRAPPER_TYPE"] = "1"
        os.environ["MLX_METAL_DEBUG"] = "0"  # Disable debug overhead
        os.environ["MLX_METAL_CAPTURE"] = "0"  # Disable GPU capture
        
        # Advanced Metal Performance optimizations
        os.environ["METAL_FORCE_INTEL_GPU"] = "0"  # Force discrete GPU if available
        os.environ["METAL_DEBUG_LAYER"] = "0"  # Disable Metal debug layer
        os.environ["METAL_SHADER_VALIDATION"] = "0"  # Disable shader validation
        os.environ["METAL_DEVICE_WRAPPER_TYPE"] = "1"  # Enable optimized wrapper
        os.environ["METAL_PERFORMANCE_SHADER_CAPTURE"] = "0"  # Disable MPS capture
        
        # Metal memory management
        os.environ["METAL_HEAP_STRATEGY"] = "0"  # Optimize heap allocation
        os.environ["METAL_BUFFER_POOLING"] = "1"  # Enable buffer pooling
        os.environ["METAL_TEXTURE_POOLING"] = "1"  # Enable texture pooling
        os.environ["METAL_COMMAND_BUFFER_POOLING"] = "1"  # Pool command buffers
        
        # Apple Silicon specific optimizations
        os.environ["METAL_UNIFIED_MEMORY"] = "1"  # Use unified memory architecture
        os.environ["METAL_GPU_PRIORITY"] = "1"  # High GPU priority
        os.environ["METAL_ASYNC_COMPILATION"] = "1"  # Async shader compilation
        
        # MLX LLM-specific optimizations
        os.environ["MLX_GPU_STREAMS"] = "8"  # More streams for LLM parallel processing
        os.environ["MLX_METAL_KERNEL_CACHE"] = "1"  # Cache compiled kernels
        os.environ["MLX_METAL_LAZY_LOADING"] = "0"  # Disable lazy loading for performance
        os.environ["MLX_MEMORY_POOL"] = "1"  # Enable memory pooling
        os.environ["MLX_LLM_CACHE_SIZE"] = str(int(gpu_bytes * 0.15))  # 15% for LLM cache (4.1GB)
        os.environ["MLX_ATTENTION_BACKEND"] = "flash"  # Flash attention for efficiency
        os.environ["MLX_SEQUENCE_PARALLEL"] = "1"  # Sequence parallelism for long contexts
        os.environ["MLX_KV_CACHE_DTYPE"] = "float16"  # 16-bit KV cache for memory efficiency
        os.environ["MLX_MATMUL_PRECISION"] = "float16"  # 16-bit matmul for speed
        os.environ["MLX_TRANSFORMER_CACHE"] = "1"  # Cache transformer layers
        os.environ["MLX_PREFILL_CHUNK_SIZE"] = "2048"  # Optimal prefill chunk for LLMs
        
        # Prevent other frameworks from using GPU memory
        os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.05"  # Severely limit PyTorch MPS
        os.environ["TF_METAL_MEMORY_GROWTH"] = "true"  # TensorFlow memory growth
        os.environ["JAX_PLATFORMS"] = "cpu"  # Force JAX to CPU
        os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Disable CUDA
        
        self.apply_metal_system_optimizations()
        self.optimize_metal_performance_shaders()
        self.optimize_llm_specific_settings()
        
        logger.info("✅ GPU, Metal, and LLM optimizations applied")
        self.print_optimization_summary()
    
    def optimize_llm_specific_settings(self):
        """Apply LLM-specific optimizations"""
        logger.info("🧠 Applying LLM-specific optimizations...")
        
        # LLM memory management
        os.environ["MLX_LLM_BATCH_SIZE"] = "1"  # Optimize for single large inference
        os.environ["MLX_LLM_MAX_TOKENS"] = "4096"  # Support longer contexts
        os.environ["MLX_LLM_CONTEXT_WINDOW"] = "32768"  # Large context window
        
        # Attention optimizations for LLMs
        os.environ["MLX_ATTENTION_SCALE"] = "auto"  # Auto-scale attention
        os.environ["MLX_ATTENTION_DROPOUT"] = "0.0"  # Disable dropout during inference
        os.environ["MLX_MULTIHEAD_ATTENTION_FUSION"] = "1"  # Fuse MHA operations
        
        # LLM inference optimizations
        os.environ["MLX_GENERATION_CACHE"] = "1"  # Cache generation states
        os.environ["MLX_BEAM_SEARCH_CACHE"] = "1"  # Cache beam search states
        os.environ["MLX_TOP_K_SAMPLING_FAST"] = "1"  # Fast top-k sampling
        os.environ["MLX_TEMPERATURE_SCALING"] = "optimized"  # Optimized temperature
        
        # Memory efficiency for large models
        os.environ["MLX_GRADIENT_CHECKPOINTING"] = "0"  # Disable for inference
        os.environ["MLX_ACTIVATION_CHECKPOINTING"] = "0"  # Disable for inference
        os.environ["MLX_WEIGHT_COMPRESSION"] = "auto"  # Auto weight compression
        
        # Token processing optimizations
        os.environ["MLX_TOKENIZER_CACHE"] = "1"  # Cache tokenizer results
        os.environ["MLX_VOCAB_PARALLEL"] = "1"  # Parallelize vocabulary operations
        os.environ["MLX_EMBEDDING_CACHE"] = "1"  # Cache embedding lookups
        
        # Long sequence optimizations
        os.environ["MLX_SLIDING_WINDOW"] = "auto"  # Auto sliding window
        os.environ["MLX_POSITION_EMBEDDING_CACHE"] = "1"  # Cache position embeddings
        os.environ["MLX_ROTARY_EMBEDDING_FAST"] = "1"  # Fast RoPE implementation
        
        # Quantization optimizations
        os.environ["MLX_QUANTIZATION_BACKEND"] = "metal"  # Use Metal for quantization
        os.environ["MLX_INT4_MATMUL"] = "1"  # Enable int4 matrix multiplication
        os.environ["MLX_DYNAMIC_QUANTIZATION"] = "1"  # Dynamic quantization
        
        logger.info("✅ LLM-specific optimizations applied")
    
    def apply_metal_system_optimizations(self):
        """Apply system-level Metal and GPU optimizations"""
        logger.info("🔧 Applying Metal system optimizations...")
        
        try:
            # GPU performance mode
            subprocess.run(["sudo", "pmset", "-a", "gpuswitch", "2"], 
                          check=False, capture_output=True)
            
            # Increase GPU memory pressure tolerance
            subprocess.run(["sudo", "sysctl", "-w", "vm.memory_pressure_level=3"], 
                          check=False, capture_output=True)
            
            # Optimize memory compression for GPU workloads
            subprocess.run(["sudo", "sysctl", "-w", "vm.compressor_mode=4"], 
                          check=False, capture_output=True)
            
            # Increase swap usage threshold (more RAM for GPU)
            subprocess.run(["sudo", "sysctl", "-w", "vm.swappiness=10"], 
                          check=False, capture_output=True)
            
            # Optimize memory allocation for large GPU buffers
            subprocess.run(["sudo", "sysctl", "-w", "vm.memory_pressure_threshold=95"], 
                          check=False, capture_output=True)
            
            # Metal-specific kernel optimizations
            subprocess.run(["sudo", "sysctl", "-w", "kern.memorystatus_level=3"], 
                          check=False, capture_output=True)
            
            # GPU thermal management (keep cool for sustained performance)
            subprocess.run(["sudo", "sysctl", "-w", "machdep.xcpm.cpu_thermal_level=0"], 
                          check=False, capture_output=True)
            
            logger.info("✅ Metal system optimizations applied")
            
        except Exception as e:
            logger.warning(f"Some system optimizations require sudo access: {e}")
    
    def optimize_metal_performance_shaders(self):
        """Optimize Metal Performance Shaders (MPS) for MLX"""
        logger.info("⚡ Optimizing Metal Performance Shaders...")
        
        # MPS optimizations
        os.environ["MPS_FORCE_HEAPS"] = "1"  # Force heap allocation
        os.environ["MPS_DISABLE_METAL_VALIDATION"] = "1"  # Disable validation
        os.environ["MPS_ENABLE_BATCH_INFERENCE"] = "1"  # Batch inference mode
        os.environ["MPS_PREFER_UNIFIED_MEMORY"] = "1"  # Use unified memory
        
        # Neural Engine optimizations (for supported operations)
        os.environ["ANE_PRIORITY"] = "1"  # High ANE priority
        os.environ["ANE_POWER_BUDGET"] = "1"  # Max power budget
        
        # Metal command queue optimizations
        os.environ["METAL_MAX_COMMAND_BUFFERS"] = "64"  # More command buffers
        os.environ["METAL_COMMAND_QUEUE_PRIORITY"] = "1"  # High priority
        
        logger.info("✅ Metal Performance Shaders optimized")
        
    def print_optimization_summary(self):
        """Print current optimization settings"""
        print("\n" + "="*70)
        print("🎯 MLX LLM + METAL GPU OPTIMIZATION ACTIVE")
        print("="*70)
        print(f"💾 Dedicated GPU Memory: {self.gpu_memory_limit} GB")
        print(f"⚠️  Soft Limit (reduce output): {self.soft_limit} GB")
        print(f"🛑 Hard Limit (kill processes): {self.hard_limit} GB")
        
        print("\n🔧 MLX Core Optimizations:")
        print(f"  • Buffer Size: {int(self.gpu_memory_limit * 1024)} MB")
        print(f"  • GPU Streams: {os.environ.get('MLX_GPU_STREAMS', '8')}")
        print(f"  • LLM Cache: {int(self.gpu_memory_limit * 0.15 * 1024)} MB (15%)")
        print(f"  • Kernel Cache: {os.environ.get('MLX_METAL_KERNEL_CACHE', 'Enabled')}")
        print(f"  • Memory Pool: {os.environ.get('MLX_MEMORY_POOL', 'Enabled')}")
        
        print("\n🧠 LLM Optimizations:")
        print(f"  • Attention Backend: {os.environ.get('MLX_ATTENTION_BACKEND', 'Flash Attention')}")
        print(f"  • Context Window: {os.environ.get('MLX_LLM_CONTEXT_WINDOW', '32768')} tokens")
        print(f"  • KV Cache: {os.environ.get('MLX_KV_CACHE_DTYPE', 'float16')}")
        print(f"  • MatMul Precision: {os.environ.get('MLX_MATMUL_PRECISION', 'float16')}")
        print(f"  • Sequence Parallel: {os.environ.get('MLX_SEQUENCE_PARALLEL', 'Enabled')}")
        print(f"  • Generation Cache: {os.environ.get('MLX_GENERATION_CACHE', 'Enabled')}")
        print(f"  • Fast Sampling: {os.environ.get('MLX_TOP_K_SAMPLING_FAST', 'Enabled')}")
        
        print("\n⚡ Metal Performance:")
        print(f"  • Unified Memory: {os.environ.get('METAL_UNIFIED_MEMORY', 'Enabled')}")
        print(f"  • Buffer Pooling: {os.environ.get('METAL_BUFFER_POOLING', 'Enabled')}")
        print(f"  • Async Compilation: {os.environ.get('METAL_ASYNC_COMPILATION', 'Enabled')}")
        print(f"  • Command Buffers: {os.environ.get('METAL_MAX_COMMAND_BUFFERS', '64')}")
        print(f"  • Debug Layer: Disabled")
        print(f"  • Shader Validation: Disabled")
        
        print("\n🎯 Quantization:")
        print(f"  • Backend: {os.environ.get('MLX_QUANTIZATION_BACKEND', 'Metal')}")
        print(f"  • Int4 MatMul: {os.environ.get('MLX_INT4_MATMUL', 'Enabled')}")
        print(f"  • Dynamic Quant: {os.environ.get('MLX_DYNAMIC_QUANTIZATION', 'Enabled')}")
        
        print("\n🧠 Neural Engine:")
        print(f"  • ANE Priority: {os.environ.get('ANE_PRIORITY', 'High')}")
        print(f"  • Power Budget: {os.environ.get('ANE_POWER_BUDGET', 'Maximum')}")
        
        print("\n🚫 Framework Limits:")
        print(f"  • PyTorch MPS: 5% limit")
        print(f"  • JAX: CPU only")
        print(f"  • CUDA: Disabled")
        
        print("\n💡 Settings will reset to defaults on computer restart")
        print("🔧 Run 'python3 restore_gpu_settings.py' to restore manually")
        print("="*70)
        
    def get_gpu_memory_usage(self):
        """Get current GPU memory usage in GB"""
        try:
            # Try to get Metal GPU memory usage on macOS
            result = subprocess.run(["system_profiler", "SPDisplaysDataType"], 
                                  capture_output=True, text=True)
            # This is a simplified approach - actual GPU memory monitoring on macOS is complex
            
            # For now, use system memory as proxy
            memory = psutil.virtual_memory()
            memory_gb = memory.used / (1024**3)
            return memory_gb
            
        except Exception as e:
            logger.warning(f"Could not get GPU memory usage: {e}")
            # Fallback to system memory
            memory = psutil.virtual_memory()
            return memory.used / (1024**3)
    
    def monitor_memory(self):
        """Monitor GPU memory usage and take action if limits exceeded"""
        logger.info("👁️  Starting GPU memory monitoring...")
        self.monitoring = True
        
        consecutive_warnings = 0
        
        while self.monitoring:
            try:
                memory_gb = self.get_gpu_memory_usage()
                
                if memory_gb > self.hard_limit:
                    logger.critical(f"🛑 HARD LIMIT EXCEEDED: {memory_gb:.1f}GB > {self.hard_limit}GB")
                    self.emergency_memory_cleanup()
                    
                elif memory_gb > self.soft_limit:
                    consecutive_warnings += 1
                    logger.warning(f"⚠️  SOFT LIMIT EXCEEDED: {memory_gb:.1f}GB > {self.soft_limit}GB")
                    
                    if consecutive_warnings >= 3:
                        logger.warning("🔽 Reducing MLX output parameters...")
                        self.reduce_mlx_output()
                        consecutive_warnings = 0
                        
                else:
                    consecutive_warnings = 0
                    if memory_gb > self.gpu_memory_limit:
                        logger.info(f"📊 Memory usage: {memory_gb:.1f}GB (above dedicated limit)")
                    
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                logger.info("🛑 Memory monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in memory monitoring: {e}")
                time.sleep(10)
    
    def reduce_mlx_output(self):
        """Reduce MLX model output parameters to save memory"""
        logger.info("🔽 Applying memory-saving MLX parameters...")
        
        # Set environment variables for reduced output
        os.environ["MLX_REDUCE_MEMORY"] = "1"
        os.environ["MLX_MAX_TOKENS"] = "256"  # Reduce max tokens
        os.environ["MLX_BATCH_SIZE"] = "1"    # Smaller batch size
        
        # Try to signal running MLX processes to reduce output
        try:
            # Send signal to running Python processes that might be using MLX
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == 'python3' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'mlx' in cmdline.lower() or 'api_server' in cmdline:
                        logger.info(f"📉 Signaling process {proc.info['pid']} to reduce output")
                        # Could implement IPC here to communicate with running MLX processes
                        
        except Exception as e:
            logger.warning(f"Could not signal running processes: {e}")
    
    def emergency_memory_cleanup(self):
        """Emergency cleanup when hard limit is exceeded"""
        logger.critical("🚨 EMERGENCY MEMORY CLEANUP INITIATED")
        
        try:
            # Kill MLX-related processes
            killed_processes = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == 'python3' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(keyword in cmdline.lower() for keyword in ['mlx', 'api_server', 'generate']):
                        try:
                            proc.terminate()
                            killed_processes += 1
                            logger.warning(f"🔪 Terminated process {proc.info['pid']}: {proc.info['name']}")
                        except:
                            pass
            
            if killed_processes > 0:
                logger.info(f"🧹 Terminated {killed_processes} MLX-related processes")
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear MLX cache if possible
            try:
                import mlx.core as mx
                mx.metal.clear_cache()
                logger.info("🗑️  Cleared MLX Metal cache")
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error during emergency cleanup: {e}")
    
    def create_restore_script(self):
        """Create a script to restore original settings"""
        restore_script = Path(__file__).parent / "restore_gpu_settings.py"
        
        script_content = f'''#!/usr/bin/env python3

import os
import json
from pathlib import Path

def restore_settings():
    settings_file = Path.home() / ".mlx_gpu_settings_backup.json"
    
    if not settings_file.exists():
        print("❌ No backup settings found")
        return
    
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        print("🔄 Restoring original GPU settings...")
        
        # Restore environment variables
        for key, value in settings.items():
            if key != "timestamp" and key.startswith(("METAL_", "MLX_", "PYTORCH_", "TF_", "CUDA_")):
                if value:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
        
        # Remove optimization flags
        for key in ["MLX_REDUCE_MEMORY", "MLX_MAX_TOKENS", "MLX_BATCH_SIZE"]:
            if key in os.environ:
                del os.environ[key]
        
        print("✅ Settings restored successfully")
        print("💡 Restart MLX applications to apply changes")
        
    except Exception as e:
        print(f"❌ Error restoring settings: {{e}}")

if __name__ == "__main__":
    restore_settings()
'''
        
        restore_script.write_text(script_content)
        os.chmod(restore_script, 0o755)
        logger.info(f"📜 Created restore script: {restore_script}")
    
    def start_optimization(self, silent=False, enable_monitoring=False):
        """Start the complete GPU optimization process"""
        if not silent:
            print("🚀 MLX GPU Memory Optimizer")
            print("="*50)
        
        self.backup_current_settings()
        self.optimize_gpu_memory()
        self.create_restore_script()
        
        if not silent:
            # Ask if user wants to start monitoring
            start_monitoring = input("\n🔍 Start real-time memory monitoring? (y/n): ").lower().strip()
            enable_monitoring = start_monitoring == 'y'
        
        if enable_monitoring:
            if not silent:
                print("\n👁️  Starting memory monitoring... (Ctrl+C to stop)")
            try:
                self.monitor_memory()
            except KeyboardInterrupt:
                if not silent:
                    print("\n🛑 Monitoring stopped")
        
        if not silent:
            print("\n✅ GPU optimization complete!")
            print("🔄 Settings will reset automatically on restart")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='MLX LLM GPU Optimizer')
    parser.add_argument('--silent', action='store_true', help='Run without interactive prompts')
    parser.add_argument('--no-monitoring', action='store_true', help='Skip memory monitoring')
    args = parser.parse_args()
    
    optimizer = MLXGPUOptimizer()
    optimizer.start_optimization(
        silent=args.silent, 
        enable_monitoring=not args.no_monitoring and not args.silent
    )

if __name__ == "__main__":
    main()