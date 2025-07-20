#!/usr/bin/env python3
"""
Test script specifically for Warp terminal integration.
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
    TerminalApp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_warp_detection():
    """Test Warp terminal detection"""
    print("\n=== Testing Warp Detection ===")
    
    bridge = AppleScriptBridge()
    
    # Check if Warp is running
    warp_running = bridge.is_application_running("Warp")
    print(f"Warp running: {warp_running}")
    
    if not warp_running:
        print("❌ Warp is not running. Please start Warp and try again.")
        return False
    
    # Try to get Warp windows
    warp_windows = bridge.get_warp_windows()
    print(f"Found {len(warp_windows)} Warp windows:")
    
    for window in warp_windows:
        print(f"  - {window.display_name} (ID: {window.id})")
    
    return len(warp_windows) > 0

def test_warp_discovery():
    """Test Warp through terminal discovery"""
    print("\n=== Testing Warp via Terminal Discovery ===")
    
    discovery = TerminalDiscovery()
    terminals = discovery.get_available_terminals(force_refresh=True)
    
    warp_terminals = [t for t in terminals if t.window.app_type == TerminalApp.WARP]
    print(f"Found {len(warp_terminals)} Warp terminals via discovery:")
    
    for terminal in warp_terminals:
        print(f"  - {terminal.window.display_name}")
        print(f"    ID: {terminal.window.id}")
        print(f"    Status: {terminal.status}")
    
    return len(warp_terminals) > 0

def test_warp_command_routing():
    """Test command routing to Warp"""
    print("\n=== Testing Warp Command Routing ===")
    
    discovery = TerminalDiscovery()
    router = CommandRouter(discovery)
    
    # Find Warp terminals
    terminals = discovery.get_available_terminals(force_refresh=True)
    warp_terminals = [t for t in terminals if t.window.app_type == TerminalApp.WARP]
    
    if not warp_terminals:
        print("❌ No Warp terminals found for command routing test")
        return False
    
    warp_terminal = warp_terminals[0]
    print(f"Testing with: {warp_terminal.window.display_name}")
    
    # Test safe command
    test_command = "echo 'Warp voice terminal test - $(date)'"
    print(f"Sending test command: {test_command}")
    
    success, message = router.route_command(test_command, warp_terminal.window.id)
    
    if success:
        print(f"✅ Command routing successful: {message}")
        
        # Check command history
        history = router.get_command_history(warp_terminal.window.id)
        print(f"Command history length: {len(history)}")
        if history:
            print(f"Last command: {history[-1]}")
        
        return True
    else:
        print(f"❌ Command routing failed: {message}")
        return False

def test_warp_target_switching():
    """Test switching targets to Warp"""
    print("\n=== Testing Warp Target Switching ===")
    
    discovery = TerminalDiscovery()
    router = CommandRouter(discovery)
    
    # Try to set Warp as target
    success = router.set_target("warp")
    print(f"Set target to 'warp': {success}")
    
    if success:
        current_target = router.get_current_target()
        print(f"Current target: {current_target}")
        
        if current_target.terminal_window and current_target.terminal_window.app_type == TerminalApp.WARP:
            print("✅ Successfully switched to Warp terminal")
            return True
        else:
            print("❌ Target not properly set to Warp")
            return False
    else:
        print("❌ Failed to set Warp as target")
        return False

def test_warp_contextual_commands():
    """Test contextual commands for Warp"""
    print("\n=== Testing Warp Contextual Commands ===")
    
    discovery = TerminalDiscovery()
    router = CommandRouter(discovery)
    
    # Test contextual command parsing
    test_queries = [
        "in warp, list files",
        "on warp 1, check status",
        "in warp 2, run tests"
    ]
    
    for query in test_queries:
        target, command = router.parse_contextual_command(query)
        print(f"Parse '{query}':")
        print(f"  Target: {target}")
        print(f"  Command: {command}")
    
    # Try executing one if Warp is available
    terminals = discovery.get_available_terminals()
    warp_terminals = [t for t in terminals if t.window.app_type == TerminalApp.WARP]
    
    if warp_terminals:
        target, command = router.parse_contextual_command("in warp, echo 'contextual test'")
        if target and command:
            print(f"\nExecuting contextual command...")
            success, message = router.route_command("echo 'contextual test'", target)
            print(f"Result: {success} - {message}")
            return success
    
    return True  # Parsing test passed even if no execution

def test_warp_aliases():
    """Test setting aliases for Warp terminals"""
    print("\n=== Testing Warp Aliases ===")
    
    discovery = TerminalDiscovery()
    terminals = discovery.get_available_terminals()
    warp_terminals = [t for t in terminals if t.window.app_type == TerminalApp.WARP]
    
    if not warp_terminals:
        print("❌ No Warp terminals for alias testing")
        return False
    
    # Set alias for first Warp terminal
    warp_terminal = warp_terminals[0]
    success = discovery.set_terminal_alias(warp_terminal.window.id, "main-warp")
    print(f"Set alias 'main-warp' for {warp_terminal.window.id}: {success}")
    
    if success:
        # Try to find by alias
        found = discovery.get_terminal_by_name("main-warp")
        if found:
            print(f"✅ Found terminal by alias: {found.window.display_name}")
            
            # Clean up
            discovery.remove_terminal_alias("main-warp")
            print("Cleaned up test alias")
            return True
        else:
            print("❌ Could not find terminal by alias")
            return False
    
    return False

def run_warp_tests():
    """Run all Warp-specific tests"""
    print("🧪 Testing Warp Terminal Integration")
    print("=" * 50)
    
    tests = [
        ("Warp Detection", test_warp_detection),
        ("Warp Discovery", test_warp_discovery),
        ("Warp Command Routing", test_warp_command_routing),
        ("Warp Target Switching", test_warp_target_switching),
        ("Warp Contextual Commands", test_warp_contextual_commands),
        ("Warp Aliases", test_warp_aliases)
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
    print("📊 WARP TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} Warp tests passed")
    
    if passed == total:
        print("🎉 All Warp tests passed! Integration is working.")
        print("\n💡 Usage Tips:")
        print("  - Say 'Switch to Warp' to target any Warp window")
        print("  - Say 'Use Warp 1' or 'Warp 2' for specific windows")
        print("  - Try 'In Warp, list files' for contextual commands")
        print("  - Set up aliases for better window identification")
        return True
    else:
        print("⚠️  Some Warp tests failed. Check output above.")
        print("\n🔧 Common issues:")
        print("  - Ensure Warp is running")
        print("  - Check accessibility permissions")
        print("  - Make sure Warp windows are visible")
        return False

def main():
    """Main entry point"""
    try:
        success = run_warp_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())