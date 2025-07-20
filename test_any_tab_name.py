#!/usr/bin/env python3
"""
Test script to verify that the voice terminal works with ANY tab name,
not just hardcoded "test tab".
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from voice_terminal_main import MultiTerminalVoiceAssistant

def test_various_tab_names():
    """Test voice commands with various tab names"""
    print("🧪 Testing Voice Commands with Various Tab Names")
    print("=" * 60)
    
    assistant = MultiTerminalVoiceAssistant()
    
    # Test various tab names that users might have
    tab_names = [
        "frontend tab",
        "backend tab", 
        "api tab",
        "database tab",
        "server tab",
        "client tab",
        "main tab",
        "dev tab",
        "prod tab",
        "staging tab",
        "my project tab",
        "work tab",
        "personal tab",
        "react tab",
        "node tab",
        "python tab",
        "docs tab",
        "terminal tab",
        "shell tab",
        "command tab"
    ]
    
    # Test send text commands
    print("\n📤 Testing 'Send Text' Commands:")
    print("-" * 40)
    
    for tab_name in tab_names[:10]:  # Test first 10
        command = f"send hello to {tab_name}"
        try:
            parsed = assistant.parse_voice_command(command)
            
            if parsed["action"] == "send_text":
                target = parsed["target"]
                text_content = parsed["text_content"]
                
                # Check if it can find a Warp terminal for this tab name
                terminal = assistant.discovery.get_terminal_by_name(target)
                found = "✅ Found Warp" if terminal and terminal.window.app_type.name == "WARP" else "❌ Not found"
                
                print(f"  '{command}' -> Target: '{target}' | {found}")
            else:
                print(f"  '{command}' -> ❌ Wrong action: {parsed['action']}")
                
        except Exception as e:
            print(f"  '{command}' -> ❌ Error: {e}")
    
    # Test contextual commands  
    print(f"\n🎯 Testing Contextual Commands ('in [tab], [command]'):")
    print("-" * 50)
    
    contextual_tests = [
        "in frontend tab, run npm start",
        "in backend tab, run python app.py", 
        "in database tab, show tables",
        "in api tab, check git status",
        "in dev tab, list files",
        "in my project tab, run tests",
        "in work tab, clear screen",
        "in python tab, activate venv"
    ]
    
    for command in contextual_tests:
        try:
            parsed = assistant.parse_voice_command(command)
            
            if parsed["action"] == "contextual_command":
                target_id = parsed["target"]
                cmd = parsed["command"]
                
                # Check if target resolves to Warp
                is_warp = target_id and "Warp:" in target_id
                status = "✅ Maps to Warp" if is_warp else f"❌ Maps to: {target_id}"
                
                print(f"  '{command}'")
                print(f"    -> Target: {target_id} | Command: '{cmd}' | {status}")
            else:
                print(f"  '{command}' -> ❌ Wrong action: {parsed['action']}")
                
        except Exception as e:
            print(f"  '{command}' -> ❌ Error: {e}")
    
    # Test switching commands
    print(f"\n🔄 Testing 'Switch To' Commands:")
    print("-" * 35)
    
    switch_tests = [
        "switch to frontend tab",
        "use backend tab",
        "switch to api tab", 
        "use my project tab",
        "switch to work tab"
    ]
    
    for command in switch_tests:
        try:
            parsed = assistant.parse_voice_command(command)
            
            if parsed["action"] == "switch_target":
                target = parsed["target"]
                
                # Check if it can find the terminal
                terminal = assistant.discovery.get_terminal_by_name(target)
                found = "✅ Found Warp" if terminal and terminal.window.app_type.name == "WARP" else "❌ Not found"
                
                print(f"  '{command}' -> Target: '{target}' | {found}")
            else:
                print(f"  '{command}' -> ❌ Wrong action: {parsed['action']}")
                
        except Exception as e:
            print(f"  '{command}' -> ❌ Error: {e}")

def test_edge_cases():
    """Test edge cases and special scenarios"""
    print(f"\n🔍 Testing Edge Cases:")
    print("-" * 25)
    
    assistant = MultiTerminalVoiceAssistant()
    
    edge_cases = [
        # Different ways to reference tabs
        "send message to tab",           # Just "tab"
        "send hello to my tab",          # "my tab"
        "send test to the main tab",     # "the main tab"
        "in tab, run command",           # Just "tab" in contextual
        "switch to tab",                 # Just "tab" for switching
        
        # Non-tab references (should NOT target Warp)
        "send hello to terminal",        # Should target Terminal.app
        "send hello to iterm",           # Should target iTerm2
        "send hello to vscode",          # Should target VS Code
        
        # Warp without "tab"
        "send hello to warp",            # Direct warp reference
        "in warp, list files",           # Direct warp contextual
        "switch to warp"                 # Direct warp switch
    ]
    
    for command in edge_cases:
        try:
            parsed = assistant.parse_voice_command(command)
            
            if parsed["action"] in ["send_text", "switch_target"]:
                target = parsed["target"]
                terminal = assistant.discovery.get_terminal_by_name(target)
                
                if terminal:
                    app_type = terminal.window.app_type.name
                    print(f"  '{command}' -> {app_type}")
                else:
                    print(f"  '{command}' -> ❌ No terminal found for '{target}'")
                    
            elif parsed["action"] == "contextual_command":
                target_id = parsed["target"]
                print(f"  '{command}' -> Target ID: {target_id}")
            else:
                print(f"  '{command}' -> Action: {parsed['action']}")
                
        except Exception as e:
            print(f"  '{command}' -> ❌ Error: {e}")

def main():
    """Main test function"""
    print("🎤 Universal Tab Name Support Test")
    print("=" * 70)
    print("Testing if voice terminal works with ANY tab name, not just 'test tab'")
    
    try:
        test_various_tab_names()
        test_edge_cases()
        
        print(f"\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print("✅ The system should now work with ANY tab name that contains 'tab'")
        print("✅ Format: '[any name] tab' will target Warp terminal")
        print("✅ Examples: 'frontend tab', 'my project tab', 'work tab', etc.")
        print("✅ Commands: 'send X to [name] tab', 'in [name] tab, [cmd]', 'switch to [name] tab'")
        print()
        print("🎯 Voice Commands You Can Use:")
        print("  'Send hello to frontend tab'")
        print("  'In backend tab, run npm start'") 
        print("  'Switch to my project tab'")
        print("  'Send message to work tab'")
        print("  'In api tab, check git status'")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())