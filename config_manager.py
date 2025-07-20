#!/usr/bin/env python3
"""
Configuration manager for Voice Terminal Assistant
Allows users to update settings without recreating config
"""

import json
from pathlib import Path

def main():
    config_file = Path.home() / ".voice_terminal_config.json"
    
    if not config_file.exists():
        print("❌ No configuration found. Run the main app first to create initial config.")
        return
        
    # Load current config
    with open(config_file, 'r') as f:
        config = json.load(f)
        
    print("🔧 Voice Terminal Assistant Configuration")
    print("=" * 40)
    print(f"Current assistant name: {config['wake_word_name'].title()}")
    print(f"Current timeout: {config['confirmation_timeout']} seconds")
    print(f"Wake phrases: {', '.join(config['wake_phrases'])}")
    
    print("\nWhat would you like to change?")
    print("1. Assistant name")
    print("2. Auto-execution timeout")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        new_name = input(f"Enter new assistant name (current: {config['wake_word_name'].title()}): ").strip()
        if new_name:
            config['wake_word_name'] = new_name.lower()
            config['wake_phrases'] = [f"hey {new_name.lower()}", f"hi {new_name.lower()}", f"hello {new_name.lower()}"]
            print(f"✅ Assistant name changed to: {new_name.title()}")
            
    elif choice == "2":
        current_timeout = config['confirmation_timeout']
        new_timeout = input(f"Enter new timeout in seconds (current: {current_timeout}): ").strip()
        try:
            if new_timeout:
                config['confirmation_timeout'] = float(new_timeout)
                print(f"✅ Timeout changed to: {config['confirmation_timeout']} seconds")
        except ValueError:
            print("❌ Invalid number entered")
            return
            
    elif choice == "3":
        print("👋 No changes made")
        return
    else:
        print("❌ Invalid choice")
        return
        
    # Save updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print("💾 Configuration saved!")

if __name__ == "__main__":
    main()