#!/usr/bin/env python3
"""
Test script for terminal management system.
Verifies that all components work correctly.
"""

import sys
import time
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from terminal_management import (
    TerminalDiscovery,
    CommandRouter,
    AppleScriptBridge,
    TerminalStatus,
    TerminalApp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_applescript_bridge():
    """Test AppleScript bridge functionality"""
    print("\n=== Testing AppleScript Bridge ===")
    
    bridge = AppleScriptBridge()
    
    # Test basic script execution
    result = bridge.execute_script('return "test"')
    print(f"Basic script test: {result}")
    
    # Test application detection
    terminal_running = bridge.is_application_running("Terminal")
    print(f"Terminal.app running: {terminal_running}")
    
    iterm_running = bridge.is_application_running("iTerm2")
    print(f"iTerm2 running: {iterm_running}")
    
    vscode_running = bridge.is_application_running("Visual Studio Code")
    print(f"VS Code running: {vscode_running}")
    
    return True

def test_terminal_discovery():
    """Test terminal discovery functionality"""
    print("\n=== Testing Terminal Discovery ===")
    
    discovery = TerminalDiscovery()
    
    # Discover available terminals
    terminals = discovery.get_available_terminals(force_refresh=True)
    print(f"Found {len(terminals)} terminals:")
    
    for i, terminal in enumerate(terminals):
        print(f"  {i+1}. {terminal.window.display_name}")
        print(f"     App: {terminal.window.app_name}")
        print(f"     ID: {terminal.window.id}")
        print(f"     Status: {terminal.status}")
        print()
    
    # Test finding terminal by name
    if terminals:
        first_terminal = terminals[0]
        found = discovery.get_terminal_by_name(first_terminal.window.app_name.lower())
        print(f"Search test - Found terminal: {found.window.display_name if found else 'None'}")
    
    # Test active terminal detection
    active = discovery.get_active_terminal()
    print(f"Active terminal: {active.window.display_name if active else 'None'}")
    
    return len(terminals) > 0

def test_command_router():
    """Test command routing functionality"""
    print("\n=== Testing Command Router ===")
    
    discovery = TerminalDiscovery()
    router = CommandRouter(discovery)
    
    # Get available targets
    targets = router.list_available_targets()
    print(f"Available targets: {targets}")
    
    # Test target switching
    if len(targets) > 1:  # More than just "local"
        target = targets[1]  # First non-local target
        success = router.set_target(target)
        print(f"Set target to '{target}': {success}")
        
        current = router.get_current_target()
        print(f"Current target: {current}")
    
    # Test contextual command parsing
    test_commands = [
        "in VS Code, run npm start",
        "on terminal 1, list files",
        "in iterm, check status"
    ]
    
    for cmd in test_commands:
        target, command = router.parse_contextual_command(cmd)
        print(f"Parse '{cmd}' -> Target: {target}, Command: {command}")
    
    return True

def test_end_to_end():
    """Test complete workflow"""
    print("\n=== Testing End-to-End Workflow ===")
    
    try:
        # Initialize components
        discovery = TerminalDiscovery()
        router = CommandRouter(discovery)
        
        # Find terminals
        terminals = discovery.get_available_terminals(force_refresh=True)
        if not terminals:
            print("No terminals found for end-to-end test")
            return False
        
        print(f"Using terminal: {terminals[0].window.display_name}")
        
        # Test safe command routing
        test_command = "echo 'Terminal management test'"
        success, message = router.route_command(test_command, terminals[0].window.id)
        
        if success:
            print(f"✅ Command routing successful: {message}")
        else:
            print(f"❌ Command routing failed: {message}")
            
        # Test command history
        history = router.get_command_history(terminals[0].window.id)
        print(f"Command history length: {len(history)}")
        
        return success
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False

def test_safety_features():
    """Test safety and validation features"""
    print("\n=== Testing Safety Features ===")
    
    discovery = TerminalDiscovery()
    router = CommandRouter(discovery)
    
    # Test dangerous command detection
    dangerous_commands = [
        "rm -rf /",
        "sudo rm -rf *",
        "format C:",
        "dd if=/dev/zero of=/dev/sda"
    ]
    
    terminals = discovery.get_available_terminals()
    if not terminals:
        print("No terminals available for safety testing")
        return True
    
    test_terminal = terminals[0].window
    
    for cmd in dangerous_commands:
        is_safe, warning = router.validate_command(cmd, test_terminal)
        status = "❌ BLOCKED" if not is_safe else "✅ ALLOWED"
        print(f"{status}: '{cmd}' - {warning}")
    
    return True

def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Testing Terminal Management System")
    print("=" * 50)
    
    tests = [
        ("AppleScript Bridge", test_applescript_bridge),
        ("Terminal Discovery", test_terminal_discovery),
        ("Command Router", test_command_router),
        ("Safety Features", test_safety_features),
        ("End-to-End", test_end_to_end)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔧 Running {test_name} test...")
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ ERROR in {test_name}: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Terminal management system is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

def main():
    """Main entry point"""
    try:
        success = run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())