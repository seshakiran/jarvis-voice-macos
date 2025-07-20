#!/usr/bin/env python3
"""
Initial configuration setup for Voice Terminal Assistant
Run this once to set up your preferences
"""

import json
from pathlib import Path

def main():
    config_file = Path.home() / ".voice_terminal_config.json"
    
    if config_file.exists():
        print("⚠️  Configuration already exists!")
        print("Use 'python3 config_manager.py' to modify settings")
        return
        
    print("🎤 Voice Terminal Assistant - Initial Setup")
    print("=" * 45)
    
    # Get assistant name
    print("\n👋 Let's set up your personal voice assistant...")
    name = input("What would you like to call your assistant? (e.g., Jarvis, Assistant, Friday): ").strip()
    if not name:
        name = "Jarvis"
        
    # Get timeout preference
    print(f"\n⏰ Command Auto-Execution Timeout")
    print("When I suggest a command, how long should I wait before executing it?")
    print("(You can always say 'no' or press 'n' to cancel)")
    
    timeout_input = input("Enter seconds (recommended: 2): ").strip()
    try:
        timeout = float(timeout_input) if timeout_input else 2.0
        if timeout < 0.5:
            print("⚠️  Minimum timeout is 0.5 seconds, setting to 0.5")
            timeout = 0.5
        elif timeout > 30:
            print("⚠️  Maximum timeout is 30 seconds, setting to 30")
            timeout = 30
    except ValueError:
        print("⚠️  Invalid input, using default 2 seconds")
        timeout = 2.0
        
    # Create configuration
    config = {
        "wake_word_name": name.lower(),
        "wake_phrases": [
            f"hey {name.lower()}", 
            f"hi {name.lower()}", 
            f"hello {name.lower()}"
        ],
        "confirmation_timeout": timeout,
        "version": "1.0"
    }
    
    # Save configuration
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Configuration saved successfully!")
        print(f"📱 Assistant name: {name.title()}")
        print(f"🗣️  Wake phrases: 'Hey {name}', 'Hi {name}', 'Hello {name}'")
        print(f"⚡ Auto-execution timeout: {timeout} seconds")
        print(f"\n🚀 You can now run: ./run.sh")
        print(f"🔧 To change settings later: python3 config_manager.py")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())