#!/usr/bin/env python3
"""
Test Standalone Systems with Dynamic Routing
Demonstrates independent operation and optional routing between AI and Context systems
"""

import requests
import json
import time
import sys

AI_URL = "http://localhost:8000"
CONTEXT_URL = "http://localhost:8001"

def test_standalone_systems():
    """Test both standalone systems and their routing capabilities"""
    
    print("🧪 Testing Standalone Systems with Dynamic Routing")
    print("=" * 60)
    
    # Test 1: Check if both systems are running independently
    print("\n1. 🔍 Checking System Availability...")
    
    ai_running = check_service(AI_URL, "MLX AI Controller")
    context_running = check_service(CONTEXT_URL, "Context Database")
    
    if not ai_running:
        print("❌ MLX AI Controller not running on port 8000")
        print("   Start with: Launch Standalone MLX AI.command")
        return
    
    if not context_running:
        print("❌ Context Database not running on port 8001")
        print("   Start with: Launch Standalone Context Database.command")
        return
    
    print("✅ Both systems are running independently!")
    
    # Test 2: Test AI Controller independently (no routing)
    print("\n2. 🤖 Testing AI Controller (Independent Mode)...")
    test_ai_independent()
    
    # Test 3: Test Context Database independently
    print("\n3. 🗄️ Testing Context Database (Independent Mode)...")
    conv_id = test_context_independent()
    
    # Test 4: Enable routing and test integration
    print("\n4. 🔗 Testing Dynamic Routing Integration...")
    test_dynamic_routing(conv_id)
    
    # Test 5: Disable routing and verify independence
    print("\n5. 🔌 Testing Routing Disable (Back to Independent)...")
    test_routing_disable()
    
    print("\n🎉 All tests completed!")
    show_usage_summary()

def check_service(url: str, name: str) -> bool:
    """Check if a service is running"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ {name}: Running")
            return True
        else:
            print(f"   ❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ {name}: Not responding")
        return False
    except Exception as e:
        print(f"   ❌ {name}: Error - {e}")
        return False

def test_ai_independent():
    """Test AI controller working independently"""
    print("   Testing independent AI generation...")
    
    payload = {
        "messages": [{"role": "user", "content": "What is artificial intelligence?"}],
        "parameters": {"temperature": 0.7, "max_length": 100}
    }
    
    try:
        response = requests.post(f"{AI_URL}/generate", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ AI Response: {result['text'][:60]}...")
            print(f"   📊 Context Enhanced: {result.get('context_enhanced', False)}")
        else:
            print(f"   ❌ AI generation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ AI test error: {e}")

def test_context_independent():
    """Test context database working independently"""
    print("   Testing independent context management...")
    
    # Create conversation
    conv_payload = {"name": "Test Research Session"}
    try:
        response = requests.post(f"{CONTEXT_URL}/conversations", json=conv_payload)
        if response.status_code == 200:
            result = response.json()
            conv_id = result['conversation_id']
            print(f"   ✅ Created conversation: {conv_id}")
            
            # Add context injection
            inject_payload = {
                "content": "You are a research assistant. Focus on practical applications.",
                "type": "system",
                "priority": 10
            }
            response = requests.post(f"{CONTEXT_URL}/conversations/{conv_id}/inject", json=inject_payload)
            if response.status_code == 200:
                print(f"   ✅ Added context injection")
            
            return conv_id
        else:
            print(f"   ❌ Context creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Context test error: {e}")
        return None

def test_dynamic_routing(conv_id: str):
    """Test dynamic routing between systems"""
    if not conv_id:
        print("   ❌ No conversation ID available for routing test")
        return
    
    print("   Testing dynamic routing connection...")
    
    # Enable routing on AI controller
    print("   🔗 Enabling context routing on AI controller...")
    toggle_payload = {"enabled": True}
    try:
        response = requests.post(f"{AI_URL}/routing/toggle", json=toggle_payload)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ Failed to enable routing: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Routing toggle error: {e}")
        return
    
    # Test AI with context routing
    print("   🧠 Testing AI with context enhancement...")
    payload = {
        "messages": [{"role": "user", "content": "What is machine learning?"}],
        "conversation_id": conv_id,
        "parameters": {"temperature": 0.7, "max_length": 150}
    }
    
    try:
        response = requests.post(f"{AI_URL}/generate", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Context-Enhanced Response: {result['text'][:60]}...")
            print(f"   🔗 Context Enhanced: {result.get('context_enhanced', False)}")
            print(f"   📝 Conversation ID: {result.get('conversation_id')}")
        else:
            print(f"   ❌ Context-enhanced generation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Context routing test error: {e}")

def test_routing_disable():
    """Test disabling routing and returning to independent mode"""
    print("   Testing routing disable...")
    
    # Disable routing on AI controller
    toggle_payload = {"enabled": False}
    try:
        response = requests.post(f"{AI_URL}/routing/toggle", json=toggle_payload)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['message']}")
            
            # Test independent AI again
            payload = {
                "messages": [{"role": "user", "content": "Test independent mode"}],
                "parameters": {"temperature": 0.7, "max_length": 50}
            }
            
            response = requests.post(f"{AI_URL}/generate", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Back to independent mode")
                print(f"   📊 Context Enhanced: {result.get('context_enhanced', False)}")
            
        else:
            print(f"   ❌ Failed to disable routing: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Routing disable error: {e}")

def show_usage_summary():
    """Show practical usage summary"""
    print("\n" + "="*60)
    print("📖 STANDALONE SYSTEMS USAGE SUMMARY")
    print("="*60)
    
    print("\n🤖 STANDALONE MLX AI CONTROLLER (Port 8000):")
    print("   Independent Operation:")
    print("     POST /generate - Direct AI responses")
    print("     POST /models/load - Load AI models")
    print("   ")
    print("   Routing Control:")
    print("     POST /routing/toggle - Enable/disable context routing")
    print("     GET /routing/status - Check routing status")
    
    print("\n🗄️ STANDALONE CONTEXT DATABASE (Port 8001):")
    print("   Independent Operation:")
    print("     POST /conversations - Create conversation contexts")
    print("     POST /conversations/<id>/inject - Add context injections")
    print("     GET /conversations - List all conversations")
    print("   ")
    print("   Enhancement Services:")
    print("     POST /context/<id>/enhance - Enhance messages with context")
    print("     POST /context/<id>/store - Store conversation data")
    
    print("\n🔗 DYNAMIC ROUTING:")
    print("   Enable: Both systems work together")
    print("   Disable: Both systems work independently")
    print("   Toggle anytime without restart")
    
    print("\n💡 PRACTICAL WORKFLOW:")
    print("   1. Start both systems independently")
    print("   2. Use AI for direct responses (fast)")
    print("   3. Create research contexts in database")
    print("   4. Enable routing for context-aware responses")
    print("   5. Disable routing for clean responses")
    
    print("\n🚀 QUICK COMMANDS:")
    print("   # Start AI Controller")
    print("   double-click 'Launch Standalone MLX AI.command'")
    print("   ")
    print("   # Start Context Database")
    print("   double-click 'Launch Standalone Context Database.command'")
    print("   ")
    print("   # Enable routing")
    print("   curl -X POST http://localhost:8000/routing/toggle -d '{\"enabled\": true}'")
    print("   ")
    print("   # Disable routing")
    print("   curl -X POST http://localhost:8000/routing/toggle -d '{\"enabled\": false}'")

if __name__ == "__main__":
    try:
        test_standalone_systems()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)