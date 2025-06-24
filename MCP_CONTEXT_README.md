# MCP Context Server - Personal Research & Study

A proper **Model Context Protocol (MCP) server** following Anthropic's specification for personal context management, research, and study workflows.

## 🎯 What This Actually Does

Unlike the previous redundant LLM controller, this is a **real MCP server** that:

- **Manages conversation context** across study sessions
- **Persists research conversations** in a local database  
- **Provides context injection** for background knowledge
- **Controls context windows** for focused discussions
- **Integrates with your existing MLX LLM** controller via configurable port

## 🚀 Quick Start

### One-Click Launch
```bash
double-click "Launch MCP Context Server.command"
```

### Command Line
```bash
# Basic start
python3 start_mcp_context.py

# Interactive setup (choose database location, LLM port)
python3 start_mcp_context.py --setup

# Custom configuration
python3 start_mcp_context.py --db-path ~/my_research/context.db --llm-port 8000
```

## 🔧 Configuration

### Database Location
- **Default**: `./context_data/conversations.db`
- **Customizable**: Choose any folder during setup
- **Portable**: Easily backup/move your research context

### LLM Integration
- **Default Port**: 8000 (your MLX controller)
- **Configurable**: Set any port for chaining
- **Chain-ready**: Use with multiple LLM services

## 🎛️ MCP Tools Available

### Context Management
- **`create_conversation`** - Start new research session
- **`add_context_injection`** - Inject background knowledge
- **`manage_context_window`** - Control conversation memory
- **`generate_with_context`** - LLM generation with managed context

### Research Features
- **Conversation persistence** - Never lose research progress
- **Context injection types**: system, background, instruction, knowledge
- **Priority-based context** - Important information stays accessible
- **Window strategies**: recent, important, semantic

## 🔗 MCP Client Integration

### Claude Desktop
Add to your Claude Desktop configuration:
```json
{
  "servers": {
    "mcp-context": {
      "command": "python3",
      "args": ["/Users/aura/AI_CORE/MLX_LLM_Controller/mcp_context_server.py"],
      "env": {}
    }
  }
}
```

### Other MCP Clients
The server follows Anthropic's MCP specification and works with any compliant client.

## 🗄️ Database Schema

### Conversations
- **id**: Unique conversation identifier
- **name**: Human-readable conversation name
- **metadata**: Custom research metadata
- **timestamps**: Created/updated tracking

### Messages
- **conversation_id**: Links to conversation
- **role**: user/assistant/system
- **content**: Message content
- **tokens**: Token count tracking

### Context Injections
- **type**: system/background/instruction/knowledge
- **content**: Injection content
- **priority**: Importance ranking
- **active**: Enable/disable toggle

## 🧪 Testing

### Run Tests
```bash
python3 test_mcp_context.py
```

Tests verify:
- ✅ MCP protocol compliance
- ✅ Database operations
- ✅ Context management
- ✅ Tool functionality

## 🎓 Example Research Workflow

### 1. Start Research Session
```bash
# Using MCP client
create_conversation("Quantum Computing Research")
```

### 2. Add Background Context
```bash
add_context_injection(
  conversation_id="abc123",
  type="background", 
  content="Focus on practical applications and current limitations",
  priority=10
)
```

### 3. Manage Context Window
```bash
manage_context_window(
  conversation_id="abc123",
  window_size=15,
  strategy="important"
)
```

### 4. Research with Context
```bash
generate_with_context(
  conversation_id="abc123",
  message="What are the latest developments in quantum error correction?",
  temperature=0.6
)
```

## 🔒 Personal Use Features

- **Local database** - Your research stays private
- **No cloud dependencies** - Works completely offline
- **Configurable storage** - Choose your own backup location
- **Research-focused** - Designed for study and analysis workflows
- **Integration-ready** - Works with your existing MLX setup

## 📁 File Structure

```
MLX_LLM_Controller/
├── mcp_context_server.py      # Core MCP server
├── start_mcp_context.py       # Launcher with setup
├── test_mcp_context.py        # Test suite
├── mcp_config.json           # Configuration
├── Launch MCP Context Server.command  # One-click launcher
└── context_data/             # Database storage (customizable)
    └── conversations.db
```

## 🎯 Why This is Better

**Before**: Redundant LLM controller that duplicated your existing functionality
**Now**: Proper MCP server that adds context management to your workflow

This integrates with your existing MLX LLM Controller instead of replacing it, providing the missing piece: **intelligent context management for research and study**.

---

**Ready to enhance your research workflow with proper context management!** 🚀