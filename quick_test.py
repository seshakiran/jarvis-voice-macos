#!/usr/bin/env python3
"""
Quick test to verify terminal discovery and text sending works
"""

from terminal_management import TerminalDiscovery, CommandRouter

def test_terminal_discovery():
    """Test terminal discovery without voice"""
    print("🔍 Testing terminal discovery...")
    
    discovery = TerminalDiscovery()
    terminals = discovery.get_available_terminals(force_refresh=True)
    
    print(f"📱 Found {len(terminals)} terminals:")
    for i, terminal in enumerate(terminals, 1):
        print(f"  {i}. {terminal.window.display_name} ({terminal.window.app_name})")
    
    return terminals

def test_text_sending(terminals):
    """Test sending text to terminals"""
    if not terminals:
        print("❌ No terminals found to test")
        return
    
    router = CommandRouter(TerminalDiscovery())
    
    # Test sending text to first terminal
    terminal = terminals[0]
    print(f"\n📤 Testing text send to: {terminal.window.display_name}")
    
    # Send a simple test message
    success, message = router.send_raw_text("echo 'Hello from voice terminal!'", terminal.window.display_name)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    terminals = test_terminal_discovery()
    test_text_sending(terminals)
    print("\n🎯 If this worked, your voice terminal is ready!")
    print("   Run: python3 voice_exec_macos.py")
    print("   Say: 'Hey Jarvis' then 'show terminals'")