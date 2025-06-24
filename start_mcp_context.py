#!/usr/bin/env python3
"""
MCP Context Server Launcher - Personal Research & Study Context Management
"""

import json
import sys
import os
import argparse
from pathlib import Path

def load_config(config_path: str = "mcp_config.json") -> dict:
    """Load MCP configuration"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config: {e}")
        return {}

def setup_database_location(config: dict) -> str:
    """Setup database location with user choice"""
    current_path = config.get("database", {}).get("path", "./context_data/conversations.db")
    
    print("🗄️  Database Location Setup")
    print("=" * 40)
    print(f"Current: {current_path}")
    print("\nOptions:")
    print("1. Keep current location")
    print("2. Choose custom location")
    print("3. Use default location")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "2":
        new_path = input("Enter database path: ").strip()
        if new_path:
            # Ensure directory exists
            Path(new_path).parent.mkdir(parents=True, exist_ok=True)
            return new_path
    elif choice == "3":
        return "./context_data/conversations.db"
    
    return current_path

def setup_llm_port(config: dict) -> int:
    """Setup LLM port with user choice"""
    current_port = config.get("llm", {}).get("port", 8000)
    
    print(f"\n🔌 LLM Connection Setup")
    print("=" * 40)
    print(f"Current port: {current_port}")
    print("\nCommon ports:")
    print("- 8000: Default MLX LLM Controller")
    print("- 3000: Alternative MLX Frontend")
    print("- 5000: Flask development")
    print("- 8080: Alternative HTTP")
    
    new_port = input(f"\nEnter LLM port [{current_port}]: ").strip()
    
    if new_port:
        try:
            return int(new_port)
        except ValueError:
            print("❌ Invalid port number, using default")
    
    return current_port

def main():
    """Main launcher"""
    parser = argparse.ArgumentParser(description="MCP Context Server for Personal Research")
    parser.add_argument("--config", default="mcp_config.json", help="Config file path")
    parser.add_argument("--db-path", help="Override database path")
    parser.add_argument("--llm-port", type=int, help="Override LLM port")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport method")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    print("🔗 MCP Context Server - Personal Research & Study")
    print("=" * 50)
    
    # Interactive setup
    if args.setup or not config:
        print("Running interactive setup...\n")
        
        # Setup database location
        db_path = setup_database_location(config)
        
        # Setup LLM port
        llm_port = setup_llm_port(config)
        
        # Update config
        config["database"]["path"] = db_path
        config["llm"]["port"] = llm_port
        
        # Save updated config
        with open(args.config, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Configuration saved to {args.config}")
    
    # Override with command line args
    db_path = args.db_path or config.get("database", {}).get("path", "./context_data/conversations.db")
    llm_port = args.llm_port or config.get("llm", {}).get("port", 8000)
    
    print(f"\n📊 Context Server Configuration:")
    print(f"   Database: {db_path}")
    print(f"   LLM Port: {llm_port}")
    print(f"   Transport: {args.transport}")
    
    # Create database directory
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🚀 Starting MCP Context Server...")
    print(f"   Use with Claude Desktop or any MCP client")
    print(f"   Context management for research & study")
    
    # Start the server
    import subprocess
    cmd = [
        sys.executable, 
        "mcp_context_server.py",
        "--db-path", db_path,
        "--llm-port", str(llm_port),
        "--transport", args.transport
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 MCP Context Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()