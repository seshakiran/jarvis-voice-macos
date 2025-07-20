#!/usr/bin/env python3
"""
Quick test script for voice command parsing without audio.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from voice_terminal_main import MultiTerminalVoiceAssistant

def test_voice_commands():
    """Test voice command parsing without audio"""
    print("🧪 Testing Voice Command Parsing")
    print("=" * 50)
    
    assistant = MultiTerminalVoiceAssistant()
    
    test_commands = [
        # Basic commands
        "list files",
        "current directory", 
        "Hey Jarvis",
        
        # Terminal management
        "list terminals",
        "switch to warp",
        "switch to test tab",
        "use terminal 1",
        
        # Text sending
        "send hello to warp",
        "send test message to terminal 1",
        "type hello to test tab",
        "say goodbye to warp",
        
        # Contextual commands
        "in warp, list files",
        "in test tab, run npm start",
        "on terminal 1, check git status",
        
        # Conversational (should be ignored)
        "thinking",
        "hello",
        "thank you",
        
        # Commands that should work
        "clear screen",
        "check git status",
        "disk space",
    ]
    
    for cmd in test_commands:
        try:
            parsed = assistant.parse_voice_command(cmd)
            shell_cmd = assistant.find_shell_command(cmd) if parsed['action'] == 'command' else None
            
            print(f"\n📝 Input: '{cmd}'")
            print(f"   Action: {parsed['action']}")
            
            if parsed['action'] == 'send_text':
                print(f"   Target: {parsed['target']}")
                print(f"   Text: '{parsed['text_content']}'")
            elif parsed['action'] == 'switch_target':
                print(f"   Target: {parsed['target']}")
            elif parsed['action'] == 'contextual_command':
                print(f"   Target: {parsed['target']}")
                print(f"   Command: {parsed['command']}")
            elif parsed['action'] == 'command' and shell_cmd:
                print(f"   Shell Command: {shell_cmd}")
            elif parsed['action'] == 'command' and shell_cmd is None:
                print(f"   Result: Conversational/Ignored")
                
        except Exception as e:
            print(f"\n❌ Error with '{cmd}': {e}")
    
    print(f"\n✅ Command parsing test completed!")
    
    # Test terminal discovery
    print(f"\n🔍 Testing Terminal Discovery")
    print("=" * 30)
    
    terminals = assistant.discovery.get_available_terminals()
    print(f"Found {len(terminals)} terminals:")
    for terminal in terminals:
        print(f"  - {terminal.window.display_name} ({terminal.window.app_name})")
    
    # Test specific searches
    search_terms = ["warp", "test", "test tab", "terminal 1", "vs code"]
    print(f"\n🎯 Testing Terminal Search")
    print("=" * 30)
    
    for term in search_terms:
        found = assistant.discovery.get_terminal_by_name(term)
        if found:
            print(f"  '{term}' -> {found.window.display_name}")
        else:
            print(f"  '{term}' -> Not found")

if __name__ == "__main__":
    test_voice_commands()