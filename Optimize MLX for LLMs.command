#!/bin/bash

# MLX LLM GPU Optimizer - One-Click Silent Execution
# Optimizes 27.5GB GPU RAM with Metal and LLM-specific settings

echo "🚀 MLX LLM GPU Optimizer - One-Click Mode"
echo "=========================================="

# Change to script directory
cd "$(dirname "$0")/scripts"

# Check if Python script exists
if [ ! -f "optimize_mlx_gpu.py" ]; then
    echo "❌ optimizer script not found"
    echo "Make sure optimize_mlx_gpu.py is in the scripts folder"
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the optimizer with no interactive prompts
echo "⚡ Applying optimizations..."
python3 optimize_mlx_gpu.py --silent --no-monitoring

# Check if optimization succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ MLX LLM Optimization Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "💾 27.5GB dedicated to GPU/MLX"
    echo "🧠 4.1GB LLM cache allocated"
    echo "⚡ Flash Attention enabled"
    echo "🎯 Int4 quantization active"
    echo "🔧 8 GPU streams for parallel processing"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔄 Settings will reset on computer restart"
    echo "🚀 Your MLX models are now optimized!"
    echo ""
    echo "Ready to launch MLX Frontend with optimized performance!"
else
    echo ""
    echo "❌ Optimization failed"
    echo "Check the error messages above"
    read -p "Press Enter to exit..."
    exit 1
fi

# Optional: Ask if user wants to launch MLX frontend
echo ""
read -p "🌐 Launch MLX Frontend now? (y/n): " launch_frontend

if [[ $launch_frontend == "y" || $launch_frontend == "Y" ]]; then
    echo "🚀 Starting MLX Frontend..."
    cd ..
    python3 start_mlx_frontend.py
else
    echo "✅ Optimization complete. You can now run MLX applications."
fi

# Keep window open briefly to show results
sleep 2