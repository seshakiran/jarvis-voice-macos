#!/usr/bin/env python3
"""
Quick test script to simulate voice commands without actual audio recording.
Useful for testing the voice terminal logic without microphone.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from voice_terminal_main import MultiTerminalVoiceAssistant

def simulate_voice_session():
    """Simulate a voice session with predefined commands"""
    print("🎤 Simulating Voice Terminal Session")
    print("=" * 50)
    
    assistant = MultiTerminalVoiceAssistant()
    
    # Simulate voice commands
    test_session = [
        "Hey Jarvis",                    # Wake word
        "list terminals",                # Show available terminals
        "switch to test tab",            # Switch to Warp  
        "list files",                    # Send ls command to Warp
        "send hello to test tab",        # Send text to Warp
        "in warp, check git status",     # Contextual command
        "current directory",             # Simple command
        "sleep"                          # End session
    ]
    
    session_active = False
    
    for i, command in enumerate(test_session):
        print(f"\n🗣️  User says: '{command}'")
        
        # Check for wake word
        if not session_active and assistant.detect_wake_word(command):
            print("   🎯 Wake word detected! Starting session...")
            session_active = True
            assistant.speak("Hello! I'm Jarvis. I'm listening for commands.")
            continue
        
        if not session_active:
            print("   💤 System sleeping, waiting for wake word...")
            continue
            
        # Parse and handle command
        try:
            parsed = assistant.parse_voice_command(command)
            print(f"   📝 Parsed: {parsed['action']}")
            
            # Handle the command
            should_continue = assistant.handle_voice_command(parsed)
            
            if not should_continue:
                print("   💤 Session ended")
                session_active = False
            else:
                print("   ✅ Command processed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        time.sleep(0.5)  # Small delay for readability
    
    print(f"\n🎉 Voice session simulation completed!")

def test_specific_commands():
    """Test specific command scenarios"""
    print(f"\n🧪 Testing Specific Command Scenarios")
    print("=" * 50)
    
    assistant = MultiTerminalVoiceAssistant()
    
    scenarios = [
        {
            "name": "Send Text to Warp",
            "command": "send hello world to test tab",
            "expected": "send_text"
        },
        {
            "name": "Contextual Command",  
            "command": "in test tab, run npm start",
            "expected": "contextual_command"
        },
        {
            "name": "Terminal Switching",
            "command": "switch to warp",
            "expected": "switch_target"
        },
        {
            "name": "File Operations",
            "command": "list all files",
            "expected": "command"
        },
        {
            "name": "Conversational Ignore",
            "command": "thinking aloud",
            "expected": "command"  # Should return None shell command
        }
    ]
    
    for scenario in scenarios:
        try:
            parsed = assistant.parse_voice_command(scenario["command"])
            shell_cmd = assistant.find_shell_command(scenario["command"]) if parsed["action"] == "command" else None
            
            print(f"\n📋 {scenario['name']}")
            print(f"   Input: '{scenario['command']}'")
            print(f"   Expected: {scenario['expected']}")
            print(f"   Got: {parsed['action']}")
            
            if parsed["action"] == "command":
                if shell_cmd:
                    print(f"   Shell: {shell_cmd}")
                else:
                    print(f"   Shell: Ignored (conversational)")
            elif parsed["action"] == "send_text":
                print(f"   Target: {parsed['target']}")
                print(f"   Text: '{parsed['text_content']}'")
            elif parsed["action"] == "contextual_command":
                print(f"   Target: {parsed['target']}")
                print(f"   Command: {parsed['command']}")
            elif parsed["action"] == "switch_target":
                print(f"   Target: {parsed['target']}")
                
            status = "✅ PASS" if parsed["action"] == scenario["expected"] else "❌ FAIL"
            print(f"   Result: {status}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

def main():
    """Main test function"""
    try:
        print("🚀 Voice Terminal Test Suite")
        print("=" * 60)
        
        # Test 1: Command scenarios
        test_specific_commands()
        
        # Test 2: Voice session simulation
        simulate_voice_session()
        
        print(f"\n✅ All tests completed successfully!")
        print(f"\n💡 To test with real voice:")
        print(f"   python3 voice_terminal_main.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())