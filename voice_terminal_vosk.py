#!/usr/bin/env python3
"""
Voice Terminal with Vosk (offline speech recognition) - much faster than Whisper
"""

import os
import sys
import json
import time
import logging
import subprocess
import pyaudio
import vosk
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

class VoskVoiceTerminalAssistant:
    """Voice assistant using Vosk offline speech recognition"""
    
    def __init__(self):
        self.config = self._load_config()
        self.tts_engine = pyttsx3.init()
        self.is_listening = False
        self.session_active = False
        self.last_activity = time.time()
        
        # Initialize Vosk
        self.vosk_model = None
        self.recognizer = None
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        
        # Initialize terminal management
        self.discovery = TerminalDiscovery()
        self.router = CommandRouter(self.discovery)
        
        # Load command mappings
        self.command_mappings = self._load_command_mappings()
        
        # Configure TTS and load Vosk model
        self._configure_tts()
        self._load_vosk_model()
        
        logger.info("Vosk Voice Terminal Assistant initialized")
    
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
            "vosk_model_path": "vosk-model-small-en-us-0.15"  # Download from https://alphacephei.com/vosk/models
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
        except Exception as e:
            logger.warning(f"TTS configuration warning: {e}")
    
    def _load_vosk_model(self):
        """Load Vosk speech recognition model"""
        try:
            model_path = self.config['vosk_model_path']
            
            # Check if model exists
            if not os.path.exists(model_path):
                logger.error(f"Vosk model not found at {model_path}")
                logger.info("Download a model from https://alphacephei.com/vosk/models")
                logger.info("For example: wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip")
                logger.info("Then unzip it in the project directory")
                # Use small model fallback
                model_path = "vosk-model-small-en-us-0.15"
                
            if os.path.exists(model_path):
                logger.info(f"Loading Vosk model from {model_path}")
                self.vosk_model = vosk.Model(model_path)
                self.recognizer = vosk.KaldiRecognizer(self.vosk_model, self.rate)
                logger.info("Vosk model loaded successfully")
            else:
                logger.error("No Vosk model found. Please download a model.")
                raise FileNotFoundError("Vosk model required")
                
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise
    
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
    
    def listen_for_speech(self, timeout: float = 5.0) -> Optional[str]:
        """Listen for speech using Vosk"""
        if not self.recognizer:
            logger.error("Vosk recognizer not initialized")
            return None
            
        try:
            logger.info(f"Listening for speech (timeout: {timeout}s)...")
            
            stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            start_time = time.time()
            frames = []
            
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    break
                    
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                
                # Process audio chunk
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    if text:
                        stream.close()
                        logger.info(f"Vosk recognized: {text}")
                        return text
            
            # Get final result
            stream.close()
            final_result = json.loads(self.recognizer.FinalResult())
            text = final_result.get('text', '').strip()
            
            if text:
                logger.info(f"Vosk final result: {text}")
                return text
            else:
                logger.debug("No speech detected")
                return None
                
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None
    
    def detect_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        if not text:
            return False
        wake_word = self.config['wake_word'].lower()
        return wake_word in text.lower()
    
    # [Include all the same parsing and command handling methods from the previous version]
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
                
                time.sleep(self.config['auto_execute_timeout'])
                
                success, message = self.router.route_command(shell_command)
                
                if not success and "Use local execution" in message:
                    success, stdout, stderr = self.execute_command_locally(shell_command)
                    if success:
                        if stdout.strip():
                            logger.info(f"Command output: {stdout}")
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
                if time.time() - self.last_activity > self.config['session_timeout']:
                    self.speak("Session timeout. Going to sleep.")
                    break
                
                transcription = self.listen_for_speech(timeout=self.config['command_timeout'])
                if not transcription:
                    continue
                
                logger.info(f"Heard: {transcription}")
                
                parsed = self.parse_voice_command(transcription)
                should_continue = self.handle_voice_command(parsed)
                
                if not should_continue:
                    break
                
                self.last_activity = time.time()
                
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
                transcription = self.listen_for_speech(timeout=3.0)
                if not transcription:
                    continue
                
                logger.info(f"Heard: {transcription}")
                
                if self.detect_wake_word(transcription):
                    logger.info("Wake word detected!")
                    self.run_session()
                
                if transcription.lower().strip() in ["exit", "quit", "shutdown"]:
                    self.speak("Shutting down voice terminal. Goodbye!")
                    break
                
            except KeyboardInterrupt:
                self.speak("Shutting down voice terminal. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Wake word detection error: {e}")
                time.sleep(1)
    
    def run(self):
        """Main application loop"""
        try:
            terminals = self.discovery.get_available_terminals()
            logger.info(f"Found {len(terminals)} terminals:")
            for terminal in terminals:
                logger.info(f"  - {terminal.window.display_name} ({terminal.window.app_name})")
            
            self.listen_for_wake_word()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.speak("Voice terminal encountered an error and will shut down.")
    
    def __del__(self):
        """Cleanup audio resources"""
        try:
            if hasattr(self, 'audio'):
                self.audio.terminate()
        except:
            pass

def main():
    """Entry point"""
    try:
        assistant = VoskVoiceTerminalAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())