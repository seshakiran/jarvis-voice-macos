#!/usr/bin/env python3
"""
Quick start script for the Multi-Terminal Voice Assistant
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'whisper',
        'sounddevice', 
        'soundfile',
        'pyttsx3'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main entry point"""
    print("🎤 Multi-Terminal Voice Assistant")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print("✅ Dependencies OK")
    print("🚀 Starting voice terminal...")
    print()
    print("Available modes:")
    print("  1. Full voice assistant (voice_terminal_main.py)")
    print("  2. Test terminal management (test_terminal_management.py)")
    print("  3. Simple voice exec (app/voice_exec.py)")
    print()
    
    try:
        choice = input("Choose mode (1-3) or Enter for default (1): ").strip()
        
        if choice == "2":
            print("Running terminal management tests...")
            subprocess.run([sys.executable, "test_terminal_management.py"])
        elif choice == "3":
            print("Starting simple voice exec...")
            subprocess.run([sys.executable, "app/voice_exec.py"])
        else:
            print("Starting full voice assistant...")
            subprocess.run([sys.executable, "voice_terminal_main.py"])
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())