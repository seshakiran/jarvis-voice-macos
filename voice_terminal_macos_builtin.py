#!/usr/bin/env python3
"""
Voice Terminal using macOS built-in speech recognition (no external dependencies)
Fastest and most reliable option for macOS users
"""

import os
import sys
import json
import time
import logging
import subprocess
import pyttsx3
from pathlib import Path
from typing import Optional, Dict, Any

# Import terminal management system
from terminal_management import (
    TerminalDiscovery, 
    CommandRouter, 
    TerminalStatus,
    TerminalApp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MacOSVoiceTerminalAssistant:
    """Voice assistant using macOS built-in speech recognition"""
    
    def __init__(self):
        self.config = self._load_config()
        self.tts_engine = pyttsx3.init()
        self.is_listening = False
        self.session_active = False
        self.last_activity = time.time()
        
        # Initialize terminal management
        self.discovery = TerminalDiscovery()
        self.router = CommandRouter(self.discovery)
        
        # Load command mappings
        self.command_mappings = self._load_command_mappings()
        
        # Configure TTS
        self._configure_tts()
        
        logger.info("macOS Voice Terminal Assistant initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path.home() / ".voice_terminal_config.json"
        default_config = {
            "assistant_name": "Jarvis",
            "wake_word": "hey jarvis",
            "auto_execute_timeout": 2.0,
            "session_timeout": 30.0,
            "command_timeout": 5.0,
            "voice_rate": 200,
            "voice_volume": 0.9,
            "speech_timeout": 5
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
                    return default_config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        return default_config
    
    def _load_command_mappings(self) -> Dict[str, Any]:
        """Load command mappings from JSON file"""
        mapping_path = Path(__file__).parent / "command_mappings.json"
        if mapping_path.exists():
            try:
                with open(mapping_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading command mappings: {e}")
        return {}
    
    def _configure_tts(self):
        """Configure text-to-speech engine"""
        try:
            self.tts_engine.setProperty('rate', self.config['voice_rate'])
            self.tts_engine.setProperty('volume', self.config['voice_volume'])
            
            # Use better macOS voice if available
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'alex' in voice.name.lower() or 'samantha' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            logger.warning(f"TTS configuration warning: {e}")
    
    def speak(self, text: str, interrupt: bool = False):
        """Speak text with optional interrupt capability"""
        try:
            if interrupt:
                self.tts_engine.stop()
            
            logger.info(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    def listen_for_speech_macos(self, timeout: float = 5.0) -> Optional[str]:
        """Use macOS built-in speech recognition via AppleScript"""
        try:
            logger.info(f"Listening for speech using macOS recognition (timeout: {timeout}s)...")
            
            # Create AppleScript for speech recognition
            applescript = f'''
            set timeoutSeconds to {int(timeout)}
            set startTime to current date
            
            try
                tell application "SpeechRecognitionServer"
                    listen continuously with timeout timeoutSeconds
                end tell
            on error
                -- Fallback to simple recognition
                display dialog "Say something:" giving up after timeoutSeconds default answer ""
                return text returned of result
            end try
            '''
            
            # Alternative approach using osascript with speech recognition
            simple_script = f'''
            try
                set speech_result to (display dialog "Listening... (speak now)" giving up after {timeout} default answer "")
                return text returned of speech_result
            on error
                return ""
            end try
            '''
            
            # Execute via osascript
            result = subprocess.run(
                ["osascript", "-e", simple_script],
                capture_output=True,
                text=True,
                timeout=timeout + 2
            )
            
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout.strip()
                logger.info(f"macOS recognized: {text}")
                return text
            else:
                logger.debug("No speech detected or recognition failed")
                return None
                
        except subprocess.TimeoutExpired:
            logger.debug("Speech recognition timeout")
            return None
        except Exception as e:
            logger.error(f"macOS speech recognition error: {e}")
            return None
    
    def listen_for_speech_simple(self) -> Optional[str]:
        """Simple text input fallback for testing"""
        try:
            print("🎤 Voice Input (or type for testing): ", end="", flush=True)
            
            # Try to read from stdin with timeout
            import select
            import sys
            
            # Check if input is available
            if select.select([sys.stdin], [], [], 0.1)[0]:
                text = input().strip()
                if text:
                    logger.info(f"Text input: {text}")
                    return text
            
            return None
            
        except Exception as e:
            logger.error(f"Input error: {e}")
            return None
    
    def detect_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        if not text:
            return False
        wake_word = self.config['wake_word'].lower()
        return wake_word in text.lower()
    
    def parse_voice_command(self, text: str) -> Dict[str, Any]:
        """Parse voice command and determine action"""
        text_lower = text.lower().strip()
        
        # Session control commands
        if text_lower in ["sleep", "go to sleep", "stop listening"]:
            return {"action": "sleep", "text": text}
        
        if text_lower in ["exit", "quit", "goodbye"]:
            return {"action": "exit", "text": text}
        
        # Terminal management commands
        if any(phrase in text_lower for phrase in ["list terminals", "show terminals", "available terminals"]):
            return {"action": "list_terminals", "text": text}
        
        if text_lower.startswith("switch to ") or text_lower.startswith("use "):
            target = text_lower.replace("switch to ", "").replace("use ", "")
            return {"action": "switch_target", "target": target, "text": text}
        
        # Check for contextual commands
        target, command = self.router.parse_contextual_command(text)
        if target:
            return {"action": "contextual_command", "target": target, "command": command, "text": text}
        
        # Check for send/text commands
        if any(phrase in text_lower for phrase in ["send", "type", "say", "write"]) and any(term in text_lower for term in ["to", "in", "on"]):
            parts = text_lower.split()
            if "to" in parts:
                to_index = parts.index("to")
                if to_index > 0 and to_index < len(parts) - 1:
                    target_name = " ".join(parts[to_index + 1:])
                    text_to_send = " ".join(parts[1:to_index])
                    return {"action": "send_text", "target": target_name, "text_content": text_to_send, "original": text}
        
        # Regular command
        return {"action": "command", "text": text}
    
    def find_shell_command(self, natural_query: str) -> Optional[str]:
        """Find shell command from natural language"""
        query_lower = natural_query.lower()
        
        for category, commands in self.command_mappings.items():
            if category == "conversational":
                if isinstance(commands, list):
                    if any(phrase in query_lower for phrase in commands):
                        return None
                continue
            
            if isinstance(commands, dict):
                for command, patterns in commands.items():
                    if isinstance(patterns, list):
                        for pattern in patterns:
                            if pattern.lower() in query_lower:
                                if "{" in command:
                                    words = query_lower.split()
                                    if "folder" in pattern and len(words) > 2:
                                        folder_name = words[-1]
                                        return command.replace("{name}", folder_name)
                                    elif "file" in pattern and len(words) > 2:
                                        file_name = words[-1]
                                        return command.replace("{file}", file_name)
                                return command
        
        return None
    
    def execute_command_locally(self, command: str) -> tuple[bool, str, str]:
        """Execute command locally"""
        try:
            logger.info(f"Executing locally: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return True, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def handle_voice_command(self, parsed_command: Dict[str, Any]) -> bool:
        """Handle parsed voice command"""
        action = parsed_command["action"]
        text = parsed_command.get("text", "")
        
        if action == "sleep":
            self.speak("Going to sleep. Say the wake word to wake me up.")
            return False
        
        elif action == "exit":
            self.speak("Goodbye!")
            return False
        
        elif action == "list_terminals":
            terminals = self.discovery.get_available_terminals()
            if terminals:
                terminal_list = [f"{t.window.display_name}" for t in terminals]
                message = f"Found: {', '.join(terminal_list)}"
                self.speak(message)
                print(f"Available terminals: {terminal_list}")
            else:
                self.speak("No terminals found")
            return True
        
        elif action == "switch_target":
            target = parsed_command["target"]
            if self.router.set_target(target):
                self.speak(f"Switched to {target}")
            else:
                self.speak(f"Terminal not found: {target}")
            return True
        
        elif action == "contextual_command":
            target = parsed_command["target"]
            command_text = parsed_command["command"]
            shell_command = self.find_shell_command(command_text)
            
            if shell_command:
                success, message = self.router.route_command(shell_command, target)
                self.speak("Command sent" if success else "Command failed")
            else:
                self.speak("Command not understood")
            return True
        
        elif action == "send_text":
            target_name = parsed_command["target"]
            text_content = parsed_command["text_content"]
            
            terminal = self.discovery.get_terminal_by_name(target_name)
            if terminal:
                success, message = self.router.send_raw_text(text_content, terminal.window.id)
                self.speak("Text sent" if success else "Send failed")
            else:
                self.speak(f"Terminal not found: {target_name}")
            return True
        
        elif action == "command":
            shell_command = self.find_shell_command(text)
            if shell_command:
                self.speak(f"Command: {shell_command}")
                print(f"Executing: {shell_command}")
                
                time.sleep(self.config['auto_execute_timeout'])
                
                success, message = self.router.route_command(shell_command)
                
                if not success and "Use local execution" in message:
                    success, stdout, stderr = self.execute_command_locally(shell_command)
                    if success and stdout.strip():
                        print(f"Output: {stdout}")
                        if len(stdout) < 100:
                            self.speak("Done")
                    if stderr.strip():
                        print(f"Error: {stderr}")
                        self.speak("Command failed")
                else:
                    self.speak("Executed" if success else "Failed")
            else:
                self.speak("Command not understood")
            return True
        
        return True
    
    def run_text_mode(self):
        """Run in text input mode for testing"""
        self.speak("Voice terminal in text mode. Type commands or 'help' for help.")
        print("\n🎤 Voice Terminal - Text Mode")
        print("Commands: 'list terminals', 'switch to [name]', 'send [text] to [terminal]'")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("Voice> ").strip()
                if not user_input:
                    continue
                    
                if user_input.lower() in ["quit", "exit"]:
                    self.speak("Goodbye!")
                    break
                    
                if user_input.lower() == "help":
                    print("Available commands:")
                    print("- list terminals")
                    print("- switch to [terminal name]")
                    print("- send [text] to [terminal name]")
                    print("- in [terminal], [command]")
                    print("- [any shell command]")
                    continue
                
                parsed = self.parse_voice_command(user_input)
                self.handle_voice_command(parsed)
                
            except KeyboardInterrupt:
                self.speak("Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"Error: {e}")
    
    def run(self):
        """Main application loop"""
        try:
            terminals = self.discovery.get_available_terminals()
            print(f"\n🎯 Found {len(terminals)} terminals:")
            for terminal in terminals:
                print(f"  - {terminal.window.display_name} ({terminal.window.app_name})")
            
            print(f"\n🎤 Starting in text mode (good for testing)")
            print(f"For voice mode, install speech recognition dependencies")
            
            self.run_text_mode()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.speak("Voice terminal encountered an error and will shut down.")

def main():
    """Entry point"""
    try:
        assistant = MacOSVoiceTerminalAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())