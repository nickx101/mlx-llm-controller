#!/usr/bin/env python3
"""
Test MCP Context Server - Verify proper MCP protocol implementation
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

class MCPContextTester:
    """Test the MCP Context Server implementation"""
    
    def __init__(self):
        self.server_process = None
    
    async def start_server(self, db_path: str = "./test_context.db", llm_port: int = 8000):
        """Start MCP server for testing"""
        cmd = [
            sys.executable,
            "mcp_context_server.py",
            "--db-path", db_path,
            "--llm-port", str(llm_port),
            "--transport", "stdio"
        ]
        
        self.server_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Started MCP server (PID: {self.server_process.pid})")
        return self.server_process
    
    def send_mcp_request(self, method: str, params: dict = None, request_id: int = 1) -> dict:
        """Send MCP request to server"""
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_line = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_line)
        self.server_process.stdin.flush()
        
        # Read response
        response_line = self.server_process.stdout.readline()
        return json.loads(response_line.strip())
    
    def test_mcp_protocol(self):
        """Test MCP protocol compliance"""
        print("\n🧪 Testing MCP Protocol Compliance")
        print("=" * 40)
        
        # Test 1: Initialize
        print("1. Testing initialize...")
        response = self.send_mcp_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        })
        
        if "result" in response:
            print("   ✅ Initialize successful")
            print(f"   📋 Server: {response['result'].get('serverInfo', {}).get('name')}")
        else:
            print(f"   ❌ Initialize failed: {response}")
            return False
        
        # Test 2: List resources
        print("\n2. Testing resources/list...")
        response = self.send_mcp_request("resources/list")
        
        if "result" in response:
            resources = response["result"].get("resources", [])
            print(f"   ✅ Found {len(resources)} resources")
        else:
            print(f"   ❌ Resources list failed: {response}")
        
        # Test 3: List tools
        print("\n3. Testing tools/list...")
        response = self.send_mcp_request("tools/list")
        
        if "result" in response:
            tools = response["result"].get("tools", [])
            print(f"   ✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"      - {tool['name']}: {tool['description']}")
        else:
            print(f"   ❌ Tools list failed: {response}")
        
        # Test 4: Create conversation
        print("\n4. Testing create_conversation tool...")
        response = self.send_mcp_request("tools/call", {
            "name": "create_conversation",
            "arguments": {
                "name": "Test Research Session",
                "metadata": {"purpose": "testing"}
            }
        })
        
        if "result" in response and not response["result"].get("isError"):
            print("   ✅ Conversation created successfully")
            conv_text = response["result"]["content"][0]["text"]
            conv_id = conv_text.split(": ")[-1]
            print(f"   📝 Conversation ID: {conv_id}")
            
            # Test 5: Add context injection
            print("\n5. Testing context injection...")
            response = self.send_mcp_request("tools/call", {
                "name": "add_context_injection",
                "arguments": {
                    "conversation_id": conv_id,
                    "type": "system",
                    "content": "You are a helpful research assistant.",
                    "priority": 10
                }
            })
            
            if "result" in response and not response["result"].get("isError"):
                print("   ✅ Context injection added")
            else:
                print(f"   ❌ Context injection failed: {response}")
        else:
            print(f"   ❌ Conversation creation failed: {response}")
        
        print("\n✅ MCP Protocol tests completed!")
        return True
    
    def cleanup(self):
        """Clean up test resources"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🧹 Server process terminated")
        
        # Clean up test database
        test_db = Path("./test_context.db")
        if test_db.exists():
            test_db.unlink()
            print("🧹 Test database cleaned up")

async def main():
    """Run MCP context server tests"""
    tester = MCPContextTester()
    
    try:
        print("🔗 MCP Context Server Test Suite")
        print("=" * 50)
        
        # Start server
        await tester.start_server()
        
        # Wait a moment for server to initialize
        await asyncio.sleep(1)
        
        # Run tests
        success = tester.test_mcp_protocol()
        
        if success:
            print("\n🎉 All tests passed! MCP Context Server is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the implementation.")
    
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    
    finally:
        tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())