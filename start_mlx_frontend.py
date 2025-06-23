#!/usr/bin/env python3

import os
import sys
import time
import subprocess
import signal
import threading
import webbrowser
from pathlib import Path

def signal_handler(signum, frame):
    print("\n🛑 Shutting down MLX Frontend...")
    os._exit(0)

def start_api_server():
    """Start the Flask API server"""
    print("🚀 Starting MLX API Server...")
    
    api_script = Path(__file__).parent / "backend" / "api_server.py"
    
    try:
        process = subprocess.Popen([
            sys.executable, str(api_script), 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], cwd=str(Path(__file__).parent / "backend"))
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_frontend_server():
    """Start a simple HTTP server for the frontend"""
    print("🌐 Starting Frontend Server...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd=str(frontend_dir))
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        return None

def wait_for_server(url, timeout=30):
    """Wait for server to be ready"""
    import requests
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🧠 MLX LLM Frontend Controller")
    print("=" * 50)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server")
        return 1
    
    time.sleep(2)
    
    # Start frontend server
    frontend_process = start_frontend_server()
    if not frontend_process:
        print("❌ Failed to start frontend server")
        api_process.terminate()
        return 1
    
    print("⏳ Waiting for servers to start...")
    time.sleep(3)
    
    # Check if API server is ready
    if wait_for_server("http://127.0.0.1:8000/health"):
        print("✅ API Server ready at http://127.0.0.1:8000")
    else:
        print("⚠️  API Server may not be ready yet")
    
    # Check if frontend server is ready  
    if wait_for_server("http://127.0.0.1:3000"):
        print("✅ Frontend Server ready at http://127.0.0.1:3000")
    else:
        print("⚠️  Frontend Server may not be ready yet")
    
    print("\n🎉 MLX Frontend is ready!")
    print("🌐 Open your browser to: http://127.0.0.1:3000")
    print("📡 API available at: http://127.0.0.1:8000")
    print("\n📋 Available models:")
    print("  • mlx-community/DeepSeek-R1-Distill-Qwen-1.5B-4bit")
    print("  • mlx-community/Qwen2.5-1.5B-Instruct-4bit") 
    print("\n💡 Usage:")
    print("  1. Load a model from the dropdown")
    print("  2. Adjust parameters using the sliders")
    print("  3. Start chatting!")
    print("\n🛑 Press Ctrl+C to stop")
    
    # Optionally open browser
    try:
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:3000")
    except:
        pass
    
    try:
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        print("\n🛑 Stopping servers...")
        if api_process:
            api_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        # Wait for processes to stop
        time.sleep(2)
        
        if api_process and api_process.poll() is None:
            api_process.kill()
        if frontend_process and frontend_process.poll() is None:
            frontend_process.kill()
            
        print("✅ Servers stopped")

if __name__ == "__main__":
    sys.exit(main())