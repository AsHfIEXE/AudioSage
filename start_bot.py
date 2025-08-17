import subprocess
import sys
import os
import time
import threading

def print_status(message):
    print(f"[STATUS] {message}")

def print_error(message):
    print(f"[ERROR] {message}")

def start_music_server():
    """Start the Node.js music server"""
    try:
        print_status("Starting Music Server (Node.js)...")
        # Check if package.json exists
        if not os.path.exists("package.json"):
            print_status("Initializing npm...")
            subprocess.run(["npm", "init", "-y"], check=True)
        
        # Check if express is installed
        if not os.path.exists("node_modules/express"):
            print_status("Installing Express...")
            subprocess.run(["npm", "install", "express"], check=True)
        
        # Start the server
        print_status("Music Server started on http://localhost:3000")
        subprocess.run(["node", "server.js"], check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to start music server: {e}")
    except FileNotFoundError:
        print_error("Node.js not found. Please install Node.js from https://nodejs.org/")
        print_error("Music server will not start, but bot can still run with existing library.")

def start_discord_bot():
    """Start the Discord bot"""
    try:
        print_status("Starting Discord Bot...")
        subprocess.run([sys.executable, "bot/main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to start Discord bot: {e}")

def start_web_ui():
    """Start the Web UI (if web directory exists)"""
    if os.path.exists("web"):
        try:
            print_status("Starting Web UI...")
            os.chdir("web")
            
            # Check if node_modules exists
            if not os.path.exists("node_modules"):
                print_status("Installing Web UI dependencies...")
                subprocess.run(["npm", "install"], check=True)
            
            print_status("Web UI started on http://localhost:3000")
            subprocess.run(["npm", "start"], check=True)
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to start Web UI: {e}")
        except FileNotFoundError:
            print_error("npm not found. Please install Node.js from https://nodejs.org/")
    else:
        print_status("Web UI directory not found. Skipping Web UI startup.")

def main():
    print("=" * 50)
    print("🎵 Advanced Music Bot - Startup Script")
    print("=" * 50)
    
    # Start services in separate threads
    threads = []
    
    # Start Music Server (in main thread to keep it running)
    music_thread = threading.Thread(target=start_music_server, daemon=True)
    music_thread.start()
    threads.append(music_thread)
    
    # Give music server time to start
    time.sleep(3)
    
    # Start Discord Bot
    bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
    bot_thread.start()
    threads.append(bot_thread)
    
    # Give bot time to start
    time.sleep(3)
    
    # Start Web UI
    web_thread = threading.Thread(target=start_web_ui, daemon=True)
    web_thread.start()
    threads.append(web_thread)
    
    print("\n" + "=" * 50)
    print("All services started!")
    print("🎵 Music Server: http://localhost:3000")
    print("🤖 Discord Bot: Running (check Discord)")
    print("🌐 Web UI: http://localhost:3001 (may take a moment)")
    print("=" * 50)
    print("Press CTRL+C to stop all services")
    print("=" * 50)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all services...")
        print("👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()