# MLX LLM Controller

A comprehensive MLX Large Language Model controller with precision parameter tuning, GPU optimization, and web-based interface for Apple Silicon.

## 🚀 Features

### 🎛️ Precision Parameter Controls
- **Temperature, Top-P, Top-K** with real-time sliders
- **Max Length, Stop Sequences** dynamic configuration  
- **Frequency/Presence Penalties** for advanced control
- **Streaming & Non-streaming** generation modes

### ⚡ GPU Memory Optimization
- **27.5GB GPU dedication** with intelligent memory management
- **Soft/Hard limits** (28.8GB/30GB) with automatic cleanup
- **Metal Performance optimization** for Apple Silicon
- **LLM-specific caching** and Flash Attention support

### 🤖 Model Management
- **Dynamic model loading/unloading** with health monitoring
- **10+ verified MLX models** including DeepSeek, Qwen, Mistral
- **Automatic model discovery** and download management
- **Quantization support** (4-bit, 8-bit) for efficiency

### 🌐 Web Interface
- **Professional responsive design** with real-time controls
- **Chat interface** with conversation history
- **Generation statistics** and performance monitoring
- **Mobile-friendly** collapsible parameter sections

## 🛠️ Installation

### Prerequisites
- **macOS** with Apple Silicon (M1/M2/M3/M4)
- **Python 3.9+** with pip
- **36GB+ RAM** recommended for optimal performance

### Quick Start
```bash
git clone https://github.com/yourusername/mlx-llm-controller.git
cd mlx-llm-controller
chmod +x "Launch MLX Frontend.command"
double-click "Launch MLX Frontend.command"
```

### Manual Installation
```bash
# Install dependencies
pip install mlx mlx-lm flask flask-cors huggingface_hub requests

# Download a model (optional)
python scripts/download_model.py "mlx-community/Qwen2.5-0.5B-Instruct-4bit"

# Start the system
python start_mlx_frontend.py
```

## 🎯 One-Click Optimization

**GPU Memory Optimization:**
```bash
double-click "Optimize MLX for LLMs.command"
```

This applies:
- 27.5GB GPU memory dedication
- 4.1GB LLM-specific cache
- Flash Attention optimization
- Metal Performance Shader tuning
- Int4 quantization support
- 8-stream parallel processing

## 📁 Project Structure

```
mlx-llm-controller/
├── backend/
│   ├── mlx_controller.py      # Core MLX integration
│   └── api_server.py          # REST API server
├── frontend/
│   ├── index.html             # Web interface
│   └── app.js                 # Frontend logic
├── scripts/
│   ├── optimize_mlx_gpu.py    # GPU optimization
│   ├── download_model.py      # Model downloader
│   └── force_download.py      # Resume downloads
├── Launch MLX Frontend.command     # One-click launcher
├── Optimize MLX for LLMs.command   # One-click optimizer
└── start_mlx_frontend.py           # Python launcher
```

## 🔧 Configuration

### Available Models
- **Qwen 2.5** (0.5B, 1.5B, 3B) - General purpose
- **DeepSeek Coder** (1.3B, 6.7B) - Code generation
- **DeepSeek R1** (8B) - Advanced reasoning  
- **Mistral 7B** - Balanced performance
- **Llama 3.2** (1B, 3B) - Meta's latest
- **Gemma 2** (2B) - Google's model

### Parameter Ranges
- **Temperature**: 0.0-2.0 (creativity control)
- **Top-P**: 0.0-1.0 (nucleus sampling)
- **Top-K**: 0-200 (vocabulary limiting)
- **Max Length**: 1-4096 tokens
- **Context Window**: Up to 32k tokens

## 🌐 API Endpoints

### Model Management
```bash
GET  /models              # List available models
POST /models/load         # Load a model
POST /models/unload       # Unload current model
GET  /health              # System health check
```

### Text Generation
```bash
POST /generate            # Generate text (non-streaming)
POST /generate/stream     # Generate text (streaming)
POST /parameters/validate # Validate parameters
GET  /parameters/defaults # Get default parameters
```

### Example API Usage
```javascript
// Load model
const response = await fetch('http://127.0.0.1:8000/models/load', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        model_path: 'mlx-community/Qwen2.5-1.5B-Instruct-4bit'
    })
});

// Generate text
const result = await fetch('http://127.0.0.1:8000/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        messages: [
            {role: 'user', content: 'Explain quantum computing'}
        ],
        parameters: {
            temperature: 0.7,
            top_p: 0.9,
            max_length: 512
        }
    })
});
```

## 🔗 Model Context Protocol (MCP) Integration

This MLX LLM Controller is designed to integrate seamlessly with the [Model Context Protocol](https://github.com/modelcontextprotocol) ecosystem:

### MCP Server Implementation
```python
# Example MCP server integration
from mcp import Server
from backend.mlx_controller import MLXController

class MLXMCPServer(Server):
    def __init__(self):
        super().__init__("mlx-llm-controller")
        self.mlx_controller = MLXController()
    
    async def handle_completion(self, request):
        return await self.mlx_controller.generate_text(
            request.messages, 
            request.parameters
        )
```

### MCP Client Usage
```javascript
// Connect to MLX LLM Controller via MCP
const client = new MCPClient();
await client.connect("mlx-llm-controller://localhost:8000");

const response = await client.complete({
    messages: [{role: "user", content: "Hello"}],
    parameters: {temperature: 0.7}
});
```

## 🚀 Performance Optimization

### Memory Management
- **Soft Limit (28.8GB)**: Reduces output parameters automatically
- **Hard Limit (30GB)**: Emergency process termination
- **Smart Caching**: 15% GPU memory for LLM operations
- **Unified Memory**: Optimized for Apple Silicon architecture

### Speed Optimizations
- **Flash Attention**: Memory-efficient attention mechanism
- **Int4 Quantization**: 4-bit integer matrix operations
- **Parallel Streams**: 8 concurrent GPU computation streams
- **Metal Optimization**: Native Apple GPU acceleration

## 📊 Monitoring & Logging

### Real-time Monitoring
```bash
# Enable monitoring (optional)
python scripts/optimize_mlx_gpu.py --enable-monitoring
```

### Log Files
- `/logs/worker.log` - MLX controller operations
- `/logs/api_server.log` - API server requests
- `/logs/model_download.log` - Model download progress

## 🛡️ Safety Features

### Automatic Recovery
- **Settings backup** before optimization
- **Auto-restore** on system restart
- **Manual restore** script available
- **Emergency cleanup** at memory limits

### Error Handling
- **Graceful degradation** on parameter errors
- **Model fallback** mechanisms
- **Network retry** logic for downloads
- **Memory pressure** monitoring

## 🔧 Development

### Running Tests
```bash
python test_system.py           # Full system test
python test_api.py             # API functionality test
python final_test.py           # Comprehensive validation
```

### Adding New Models
1. Add model name to `backend/api_server.py` model list
2. Test with: `python scripts/download_model.py <model_name>`
3. Verify compatibility with MLX-LM

### Customizing Parameters
Edit `backend/mlx_controller.py` `GenerationParams` class to add new parameters or modify validation ranges.

## 📱 Mobile Support

The web interface is fully responsive and supports:
- **Touch controls** for parameter sliders
- **Mobile keyboards** for text input
- **Collapsible sections** for small screens
- **Gesture navigation** for chat history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

### Code Style
- Follow existing patterns and conventions
- Add logging for new features
- Include error handling and validation
- Update documentation for API changes

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Apple MLX Team** for the excellent ML framework
- **Hugging Face** for model hosting and transformers
- **Model Context Protocol** for standardized AI interfaces
- **Open Source Community** for continuous improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mlx-llm-controller/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mlx-llm-controller/discussions)
- **MCP Integration**: [Model Context Protocol Documentation](https://github.com/modelcontextprotocol)

---

**Built for the Model Context Protocol ecosystem with ❤️ on Apple Silicon**