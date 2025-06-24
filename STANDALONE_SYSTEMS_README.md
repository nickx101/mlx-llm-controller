# Standalone MLX Systems with Dynamic Routing

Two completely independent systems that can optionally route to each other with a simple toggle.

## 🎯 What You Have

### 🤖 **Standalone MLX AI Controller** (Port 8000)
- **Independent AI** with precision parameter controls
- **Works alone** - no dependencies on context system
- **Optional routing** - can fetch context when toggle enabled
- **Direct responses** - clean AI answers when routing disabled

### 🗄️ **Standalone Context Database** (Port 8001)  
- **Independent context management** with conversation persistence
- **Works alone** - manages conversations and context injections
- **Optional routing** - can enhance messages for AI when toggle enabled
- **Pure storage** - database operations when routing disabled

## 🚀 Quick Start

### Start Both Systems
```bash
# Terminal 1: Start AI Controller
double-click "Launch Standalone MLX AI.command"

# Terminal 2: Start Context Database  
double-click "Launch Standalone Context Database.command"
```

### Test the Integration
```bash
python3 test_standalone_routing.py
```

## 🔗 Dynamic Routing Control

### Enable Integration
```bash
# Enable context routing on AI (AI → Context)
curl -X POST http://localhost:8000/routing/toggle -d '{"enabled": true}'

# Enable AI routing on Context (Context → AI) [optional]
curl -X POST http://localhost:8001/routing/toggle -d '{"enabled": true}'
```

### Disable Integration (Back to Independent)
```bash
# Disable context routing on AI
curl -X POST http://localhost:8000/routing/toggle -d '{"enabled": false}'

# Disable AI routing on Context
curl -X POST http://localhost:8001/routing/toggle -d '{"enabled": false}'
```

## 💡 Usage Patterns

### Pattern 1: Independent AI (Fast & Clean)
```bash
# AI works alone - direct responses
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is AI?"}]}'
```

### Pattern 2: Context-Enhanced AI (Research Mode)
```bash
# 1. Create research context
curl -X POST http://localhost:8001/conversations \
  -d '{"name": "AI Research"}'

# 2. Add background context
curl -X POST http://localhost:8001/conversations/abc123/inject \
  -d '{"content": "Focus on practical applications"}'

# 3. Enable AI routing
curl -X POST http://localhost:8000/routing/toggle -d '{"enabled": true}'

# 4. Generate with context
curl -X POST http://localhost:8000/generate \
  -d '{"messages": [{"role": "user", "content": "What is AI?"}], "conversation_id": "abc123"}'
```

### Pattern 3: Pure Context Management
```bash
# Context database works independently
curl -X POST http://localhost:8001/conversations \
  -d '{"name": "Research Notes"}'

curl -X POST http://localhost:8001/conversations/xyz789/inject \
  -d '{"content": "Important research context"}'
```

## 📡 API Endpoints

### 🤖 AI Controller (localhost:8000)
```
POST /generate              # Generate text (with optional context)
POST /models/load           # Load AI models
GET  /models               # List available models
POST /routing/toggle       # Enable/disable context routing
GET  /routing/status       # Check routing status
GET  /health               # System health
```

### 🗄️ Context Database (localhost:8001)
```
POST /conversations                    # Create conversation
GET  /conversations                    # List conversations
POST /conversations/<id>/inject        # Add context injection
GET  /conversations/<id>/messages      # Get conversation history
POST /context/<id>/enhance             # Enhance messages (for AI routing)
POST /context/<id>/store               # Store messages (for AI routing)
POST /routing/toggle                   # Enable/disable AI routing
GET  /stats                           # Database statistics
GET  /health                          # System health
```

## 🎛️ Configuration

### AI Controller Configuration
```bash
python3 standalone_mlx_controller.py \
  --host localhost \
  --port 8000 \
  --context-host localhost \
  --context-port 8001
```

### Context Database Configuration
```bash
python3 standalone_context_database.py \
  --host localhost \
  --port 8001 \
  --db-path ./context_data/conversations.db \
  --ai-host localhost \
  --ai-port 8000
```

## 🧪 Testing

### Full Integration Test
```bash
python3 test_standalone_routing.py
```

This tests:
- ✅ Independent AI operation
- ✅ Independent context operation  
- ✅ Dynamic routing enable/disable
- ✅ Context-enhanced AI responses
- ✅ Return to independent mode

### Manual Testing
```bash
# Check AI health
curl http://localhost:8000/health

# Check Context health  
curl http://localhost:8001/health

# Check routing status
curl http://localhost:8000/routing/status
curl http://localhost:8001/routing/status
```

## 🔄 Routing Flow

### When Routing Enabled:
1. **User** → **AI Controller** with conversation_id
2. **AI Controller** → **Context Database** (fetch context)
3. **Context Database** → **AI Controller** (enhanced messages)
4. **AI Controller** → **LLM** (context-enhanced generation)
5. **AI Controller** → **Context Database** (store response)
6. **AI Controller** → **User** (final response)

### When Routing Disabled:
1. **User** → **AI Controller**
2. **AI Controller** → **LLM** (direct generation)
3. **AI Controller** → **User** (direct response)

## 🎯 Perfect For:

- **Research sessions** - Enable routing for context memory
- **Quick questions** - Disable routing for fast responses  
- **Context building** - Use database independently to build research contexts
- **Flexible workflows** - Toggle between modes without restart

## 🏗️ Architecture Benefits

✅ **True Independence** - Each system works alone  
✅ **Optional Integration** - Connect when needed  
✅ **No Interference** - Routing doesn't affect core functionality  
✅ **Dynamic Control** - Toggle without restart  
✅ **Scalable** - Can add more systems with same pattern  

**Perfect separation of concerns with optional collaboration! 🎉**