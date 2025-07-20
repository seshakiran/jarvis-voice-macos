#!/usr/bin/env python3
"""
Multi-Terminal Voice Assistant - Main Application
Integrates voice recognition with multi-terminal command routing.
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Any

import sounddevice as sd
import soundfile as sf
import whisper
import pyttsx3

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

class MultiTerminalVoiceAssistant:
    """Main voice assistant with multi-terminal support"""
    
    def __init__(self):
        self.config = self._load_config()
        self.whisper_model = None
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
        
        logger.info("Multi-Terminal Voice Assistant initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path.home() / ".voice_terminal_config.json"
        default_config = {
            "assistant_name": "Jarvis",
            "wake_word": "hey jarvis",
            "auto_execute_timeout": 2.0,
            "session_timeout": 30.0,
            "command_timeout": 5.0,
            "whisper_model": "base",
            "voice_rate": 200,
            "voice_volume": 0.9
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
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
            
            # Try to set a better voice
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower() and 'female' in voice.name.lower():
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
    
    def load_whisper_model(self):
        """Load Whisper model (lazy loading)"""
        if not self.whisper_model:
            try:
                logger.info(f"Loading Whisper model: {self.config['whisper_model']}")
                self.whisper_model = whisper.load_model(self.config['whisper_model'])
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
    
    def record_audio(self, duration: float = 5.0, samplerate: int = 16000) -> Optional[str]:
        """Record audio and save to temporary file"""
        try:
            filename = "temp_voice_input.wav"
            logger.info(f"Recording audio for {duration} seconds...")
            
            recording = sd.rec(
                int(duration * samplerate),
                samplerate=samplerate,
                channels=1
            )
            sd.wait()
            
            sf.write(filename, recording, samplerate)
            return filename
        except Exception as e:
            logger.error(f"Audio recording error: {e}")
            return None
    
    def transcribe_audio(self, filename: str) -> Optional[str]:
        """Transcribe audio file using Whisper"""
        try:
            if not self.whisper_model:
                self.load_whisper_model()
            
            result = self.whisper_model.transcribe(filename)
            transcription = result["text"].strip()
            logger.info(f"Transcribed: {transcription}")
            return transcription
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def detect_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
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
        
        # Check for contextual commands (e.g., "in VS Code, run npm start" or "send hello to warp")
        target, command = self.router.parse_contextual_command(text)
        if target:
            return {"action": "contextual_command", "target": target, "command": command, "text": text}
        
        # Check for send/text commands to specific terminals
        if any(phrase in text_lower for phrase in ["send", "type", "say", "write"]) and any(term in text_lower for term in ["to", "in", "on"]):
            # Try to extract target and text: "send hello to warp"
            parts = text_lower.split()
            if "to" in parts:
                to_index = parts.index("to")
                if to_index > 0 and to_index < len(parts) - 1:
                    target_name = " ".join(parts[to_index + 1:])
                    text_to_send = " ".join(parts[1:to_index])  # Skip first word (send/type/etc)
                    return {"action": "send_text", "target": target_name, "text_content": text_to_send, "original": text}
        
        # Regular command
        return {"action": "command", "text": text}
    
    def find_shell_command(self, natural_query: str) -> Optional[str]:
        """Find shell command from natural language using multiple methods"""
        # First try command mappings
        query_lower = natural_query.lower()
        
        for category, commands in self.command_mappings.items():
            # Skip conversational patterns (they're just a list, not commands)
            if category == "conversational":
                if isinstance(commands, list):
                    # Check if this is just conversational - return None to ignore
                    if any(phrase in query_lower for phrase in commands):
                        return None
                continue
            
            # Process command mappings (dict format)
            if isinstance(commands, dict):
                for command, patterns in commands.items():
                    if isinstance(patterns, list):
                        for pattern in patterns:
                            if pattern.lower() in query_lower:
                                # Handle parameterized commands
                                if "{" in command:
                                    # Simple parameter extraction
                                    words = query_lower.split()
                                    if "folder" in pattern and len(words) > 2:
                                        folder_name = words[-1]
                                        return command.replace("{name}", folder_name)
                                    elif "file" in pattern and len(words) > 2:
                                        file_name = words[-1]
                                        return command.replace("{file}", file_name)
                                return command
        
        # Fallback to shell-genie if available
        try:
            result = subprocess.run(
                ["shell-genie", "ask", natural_query],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return None
    
    def execute_command_locally(self, command: str) -> tuple[bool, str, str]:
        """Execute command locally and return (success, stdout, stderr)"""
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
        """Handle parsed voice command. Returns True to continue session."""
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
                terminal_list = [f"{i+1}. {t.window.display_name}" for i, t in enumerate(terminals)]
                message = f"Available terminals: {', '.join(terminal_list)}"
                self.speak(message)
            else:
                self.speak("No terminals found")
            return True
        
        elif action == "switch_target":
            target = parsed_command["target"]
            if self.router.set_target(target):
                self.speak(f"Switched to {target}")
            else:
                self.speak(f"Could not find terminal: {target}")
            return True
        
        elif action == "contextual_command":
            target = parsed_command["target"]
            command_text = parsed_command["command"]
            shell_command = self.find_shell_command(command_text)
            
            if shell_command:
                success, message = self.router.route_command(shell_command, target)
                if success:
                    self.speak(f"Command sent: {shell_command}")
                else:
                    self.speak(f"Failed to send command: {message}")
            else:
                self.speak("Could not understand the command")
            return True
        
        elif action == "send_text":
            target_name = parsed_command["target"]
            text_content = parsed_command["text_content"]
            
            # Find the terminal by name
            terminal = self.discovery.get_terminal_by_name(target_name)
            if terminal:
                success, message = self.router.send_raw_text(text_content, terminal.window.id)
                if success:
                    self.speak(f"Sent '{text_content}' to {terminal.window.display_name}")
                else:
                    self.speak(f"Failed to send text: {message}")
            else:
                self.speak(f"Could not find terminal: {target_name}")
            return True
        
        elif action == "command":
            shell_command = self.find_shell_command(text)
            if shell_command:
                self.speak(f"Suggested command: {shell_command}")
                
                # Auto-execute after timeout
                time.sleep(self.config['auto_execute_timeout'])
                
                # Try to route to current target
                success, message = self.router.route_command(shell_command)
                
                if not success and "Use local execution" in message:
                    # Execute locally
                    success, stdout, stderr = self.execute_command_locally(shell_command)
                    if success:
                        if stdout.strip():
                            logger.info(f"Command output: {stdout}")
                            # Don't speak long outputs
                            if len(stdout) < 200:
                                self.speak("Command completed")
                        if stderr.strip():
                            logger.warning(f"Command stderr: {stderr}")
                    else:
                        self.speak(f"Command failed: {stderr}")
                else:
                    self.speak("Command executed" if success else f"Failed: {message}")
            else:
                self.speak("I don't understand that command")
            return True
        
        return True
    
    def run_session(self):
        """Run active voice command session"""
        self.session_active = True
        self.last_activity = time.time()
        
        self.speak(f"Hello! I'm {self.config['assistant_name']}. I'm listening for commands.")
        
        while self.session_active:
            try:
                # Check session timeout
                if time.time() - self.last_activity > self.config['session_timeout']:
                    self.speak("Session timeout. Going to sleep.")
                    break
                
                # Record audio
                audio_file = self.record_audio(duration=self.config['command_timeout'])
                if not audio_file:
                    continue
                
                # Transcribe
                transcription = self.transcribe_audio(audio_file)
                if not transcription:
                    continue
                
                # Parse and handle command
                parsed = self.parse_voice_command(transcription)
                should_continue = self.handle_voice_command(parsed)
                
                if not should_continue:
                    break
                
                self.last_activity = time.time()
                
                # Clean up audio file
                try:
                    os.unlink(audio_file)
                except:
                    pass
                
            except KeyboardInterrupt:
                self.speak("Interrupted. Going to sleep.")
                break
            except Exception as e:
                logger.error(f"Session error: {e}")
                self.speak("Sorry, I encountered an error.")
        
        self.session_active = False
    
    def listen_for_wake_word(self):
        """Listen continuously for wake word"""
        self.speak(f"Voice terminal ready. Say '{self.config['wake_word']}' to activate.")
        
        while True:
            try:
                # Record short audio clip
                audio_file = self.record_audio(duration=3.0)
                if not audio_file:
                    continue
                
                # Transcribe
                transcription = self.transcribe_audio(audio_file)
                if not transcription:
                    continue
                
                # Check for wake word
                if self.detect_wake_word(transcription):
                    logger.info("Wake word detected!")
                    self.run_session()
                
                # Check for exit command
                if transcription.lower().strip() in ["exit", "quit", "shutdown"]:
                    self.speak("Shutting down voice terminal. Goodbye!")
                    break
                
                # Clean up
                try:
                    os.unlink(audio_file)
                except:
                    pass
                
            except KeyboardInterrupt:
                self.speak("Shutting down voice terminal. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Wake word detection error: {e}")
                time.sleep(1)
    
    def run(self):
        """Main application loop"""
        try:
            # Initialize Whisper model
            self.load_whisper_model()
            
            # Show available terminals
            terminals = self.discovery.get_available_terminals()
            logger.info(f"Found {len(terminals)} terminals:")
            for terminal in terminals:
                logger.info(f"  - {terminal.window.display_name} ({terminal.window.app_name})")
            
            # Start listening for wake word
            self.listen_for_wake_word()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.speak("Voice terminal encountered an error and will shut down.")

def main():
    """Entry point"""
    try:
        assistant = MultiTerminalVoiceAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())