# MCP Control Guide - How to Control MLX LLM

## 🎛️ What is MCP Control?

**Model Context Protocol (MCP) Control** gives you multiple ways to control your MLX LLM system:

1. **🌐 Web Interface** - Visual controls with sliders and chat
2. **💻 Command Line** - Terminal commands for automation  
3. **🐍 Python API** - Programmatic control for custom scripts
4. **🔌 REST API** - HTTP endpoints for integration

## 🚀 Quick Start

### Start the MCP System
```bash
cd /Users/aura/AI_CORE/MLX_LLM_Controller
python3 start_mcp.py
```

This launches:
- ✅ MCP Server on http://localhost:8001
- ✅ Web interface automatically opens
- ✅ All control methods become available

## 🌐 Web Interface Control

### Access
- **URL**: http://localhost:8001
- **Mobile-friendly** responsive design
- **Real-time updates** and monitoring

### Features
- **📋 Model Management**: Dropdown to select and load models
- **🎚️ Parameter Controls**: Sliders for Temperature, Top-P, Top-K, Max Length
- **💬 Interactive Chat**: Full conversation interface
- **📊 System Status**: Health monitoring and GPU optimization
- **✅ Parameter Validation**: Real-time parameter checking

### Usage
1. **Load a Model**: Select from dropdown → Click "Load Model"
2. **Adjust Parameters**: Use sliders to set Temperature (0.0-2.0), Top-P (0.0-1.0), etc.
3. **Start Chatting**: Type in chat box → Press Send
4. **Monitor System**: Check status panel for health and performance

## 💻 Command Line Control

### Interactive Chat
```bash
python3 mcp_control.py --chat
```
- **Interactive session** with command support
- **Parameter controls**: `/set temperature 0.8`
- **Model management**: `/load mlx-community/Qwen2.5-1.5B-Instruct-4bit`
- **System commands**: `/models`, `/info`, `/health`

### Direct Commands
```bash
# List available models
python3 mcp_control.py models

# Load a specific model
python3 mcp_control.py load --model "mlx-community/Qwen2.5-1.5B-Instruct-4bit"

# Generate text with custom parameters
python3 mcp_control.py generate --prompt "Explain quantum computing" \
    --temperature 0.7 --max-length 512 --top-p 0.9

# Check system health
python3 mcp_control.py health

# Optimize GPU settings
python3 mcp_control.py optimize
```

### Command Options
- `--temperature 0.7` - Creativity control (0.0-2.0)
- `--top-p 0.9` - Nucleus sampling (0.0-1.0)  
- `--top-k 50` - Token limit (0-200)
- `--max-length 512` - Max output tokens (1-4096)

## 🐍 Python API Control

### Basic Usage
```python
import asyncio
from mcp_control import MCPController

async def main():
    # Initialize controller
    controller = MCPController()
    
    # List and load models
    models = await controller.list_models()
    await controller.load_model(models[0]['id'])
    
    # Generate text
    response = await controller.generate_text(
        "Explain machine learning",
        temperature=0.7,
        max_length=300
    )
    print(response)

asyncio.run(main())
```

### Interactive Chat Session
```python
import asyncio
from mcp_control import MCPController

async def chat_session():
    controller = MCPController()
    
    # Start interactive chat with default parameters
    await controller.chat_session(
        temperature=0.7,
        top_p=0.9,
        max_length=512
    )

asyncio.run(chat_session())
```

### Advanced Usage
```python
async def advanced_control():
    controller = MCPController()
    
    # Health check
    health = await controller.health_check()
    print(f"System status: {health}")
    
    # Model management
    await controller.load_model("mlx-community/Qwen2.5-1.5B-Instruct-4bit")
    info = await controller.get_model_info()
    print(f"Model info: {info}")
    
    # Generate with specific parameters
    response = await controller.generate_text(
        "Write a Python function to calculate fibonacci numbers",
        temperature=0.3,  # Low for code generation
        max_length=1024,
        top_p=0.8
    )
    print(response)
```

## 🔌 REST API Control

### Endpoints

**Model Management:**
```bash
# List models
curl http://localhost:8001/mcp/models

# Load model
curl -X POST http://localhost:8001/mcp/models/load \
  -H "Content-Type: application/json" \
  -d '{"model_id": "mlx-community/Qwen2.5-1.5B-Instruct-4bit"}'

# Unload model
curl -X POST http://localhost:8001/mcp/models/unload
```

**Text Generation:**
```bash
# Generate text
curl -X POST http://localhost:8001/mcp/generate \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Explain AI"}],
    "parameters": {
      "temperature": 0.7,
      "top_p": 0.9,
      "max_length": 512
    }
  }'
```

**System Control:**
```bash
# Health check
curl http://localhost:8001/mcp/health

# Optimize GPU
curl -X POST http://localhost:8001/mcp/optimize

# Get status
curl http://localhost:8001/mcp/status
```

## 🎯 Use Cases

### For Students & Researchers
- **📚 Study Assistant Integration**: Use with study_assistant.py
- **🔬 Research Automation**: Script multiple queries with different parameters
- **📊 Parameter Exploration**: Test different creativity levels systematically

### For Developers
- **🔗 API Integration**: Embed in other applications
- **🤖 Chatbot Development**: Build custom interfaces
- **⚡ Batch Processing**: Automate text generation tasks

### For System Administrators
- **📈 Monitoring**: Track system health and performance
- **🎛️ Remote Control**: Manage models without direct access
- **🔧 Optimization**: GPU tuning and memory management

## 🛠️ Troubleshooting

### MCP Server Won't Start
```bash
# Check dependencies
python3 -c "import flask, mlx; print('Dependencies OK')"

# Check port availability
lsof -i :8001

# Start with debug
python3 mcp_server.py --debug
```

### Web Interface Not Loading
1. **Check URL**: Ensure http://localhost:8001 is correct
2. **Check firewall**: Allow port 8001
3. **Check browser**: Try different browser or incognito mode

### Command Line Errors
```bash
# Verify files exist
ls mcp_control.py mcp_server.py mcp_integration.py

# Check permissions
chmod +x mcp_control.py start_mcp.py

# Test individual components
python3 -c "from mcp_integration import MLXMCPServer; print('OK')"
```

### Model Loading Issues
1. **Check model exists**: `python3 mcp_control.py models`
2. **Verify MLX backend**: Ensure MLX controller works
3. **Check memory**: Ensure sufficient RAM/GPU memory

## 🎉 Examples

### Research Workflow
```bash
# 1. Start system
python3 start_mcp.py

# 2. Load research model
python3 mcp_control.py load --model "mlx-community/DeepSeek-R1-0528-Qwen3-8B-4bit"

# 3. Research with different creativity levels
python3 mcp_control.py generate --prompt "Latest developments in quantum computing" --temperature 0.3
python3 mcp_control.py generate --prompt "Creative applications of quantum computing" --temperature 0.8
```

### Code Generation
```bash
# Load code-focused model
python3 mcp_control.py load --model "mlx-community/deepseek-coder-1.3b-instruct-mlx"

# Generate code with low temperature for accuracy
python3 mcp_control.py generate \
  --prompt "Write a Python class for managing ML experiments" \
  --temperature 0.2 --max-length 1024
```

### Interactive Learning
```bash
# Start chat session with optimal learning parameters
python3 mcp_control.py --chat --temperature 0.6 --max-length 800
```

---

## 🎓 Summary

MCP Control gives you **4 powerful ways** to control your MLX LLM:

1. **🌐 Web Interface** - Perfect for interactive use and parameter exploration
2. **💻 Command Line** - Ideal for automation and scripting  
3. **🐍 Python API** - Best for custom applications and integration
4. **🔌 REST API** - Great for web applications and remote control

**Choose the method that best fits your workflow!**