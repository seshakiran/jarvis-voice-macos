#!/usr/bin/env python3
"""
macOS Native Voice Terminal Assistant
Optimized for local processing without Docker
"""

import subprocess
import sounddevice as sd
import soundfile as sf
import whisper
import pyttsx3
import os
import tempfile
import json
import signal
import threading
import time
from pathlib import Path

class VoiceTerminal:
    def __init__(self):
        # Configuration file
        self.config_file = Path.home() / ".voice_terminal_config.json"
        
        # Load or create configuration
        self.config = self.load_config()
        
        # Cache Whisper model (fix from original)
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        
        # Initialize TTS
        self.engine = pyttsx3.init()
        
        # Set up temp directory
        self.temp_dir = Path(tempfile.gettempdir())
        
        # Auto-confirmation timeout from config
        self.confirmation_timeout = self.config.get("confirmation_timeout", 2)
        
        # Session management
        self.session_active = False
        self.session_timeout = 30  # seconds of inactivity before returning to wake word mode
        self.command_wait_timeout = 5  # seconds to wait for command before prompting (reduced)
        
    def speak(self, text):
        """Text-to-speech output"""
        print(f"🔊 {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        # Add longer delay after TTS to prevent microphone pickup
        time.sleep(2)
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            
        # No config found
        print("❌ No configuration found!")
        print("Please run initial setup first: python3 setup_config.py")
        exit(1)
        
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
            
    def detect_wake_word(self, text):
        """Check if text contains wake word"""
        text_lower = text.lower().strip()
        return any(phrase in text_lower for phrase in self.config["wake_phrases"])
        
    def auto_confirm_with_timeout(self, prompt, timeout=None):
        """Get user confirmation with auto-timeout"""
        if timeout is None:
            timeout = self.confirmation_timeout
            
        print(f"{prompt} [y/N] (auto-yes in {timeout}s): ", end="", flush=True)
        
        result = {'confirmed': False, 'input_received': False}
        
        def get_input():
            try:
                user_input = input().lower().strip()
                result['input_received'] = True
                result['confirmed'] = user_input in ['y', 'yes']
            except (EOFError, KeyboardInterrupt):
                result['input_received'] = True
                result['confirmed'] = False
                
        input_thread = threading.Thread(target=get_input)
        input_thread.daemon = True
        input_thread.start()
        
        # Use time.sleep instead of join for more reliable timeout
        start_time = time.time()
        while time.time() - start_time < timeout and not result['input_received']:
            time.sleep(0.1)
            
        if not result['input_received']:
            print("\n⏰ Auto-confirming due to timeout...")
            result['confirmed'] = True
            
        return result['confirmed']
        
    def clear_screen(self):
        """Clear screen and show header"""
        os.system('clear' if os.name == 'posix' else 'cls')
        wake_name = self.config["wake_word_name"].title()
        print(f"🎤 {wake_name} Voice Terminal Assistant")
        print(f"Say '{self.config['wake_phrases'][0]}' to activate")
        print("=" * 50)
        
    def record_voice_activated(self, threshold=0.01, max_duration=10, silent_mode=False, timeout=None):
        """
        Records audio with voice activation detection - simplified version
        """
        if not silent_mode:
            print("🎤 Listening... (speak now)")
            self.speak("Listening")
        
        if timeout is None:
            timeout = max_duration
            
        try:
            # Simple fixed-duration recording for reliability
            samplerate = 44100
            duration = min(timeout, 5)  # Max 5 seconds per recording
            
            if not silent_mode:
                print(f"⏺️ Recording for {duration} seconds...", end="", flush=True)
            recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
            sd.wait()  # Wait until recording is finished
            if not silent_mode:
                print("\r✅ Recording complete         ")
            
            # Check if there's actual audio (not just silence)
            max_amplitude = float(recording.max())
            # Higher threshold to avoid picking up TTS feedback
            speech_threshold = max(threshold, 0.02)
            
            if max_amplitude > speech_threshold:
                audio_file = self.temp_dir / "voice_input.wav"
                sf.write(audio_file, recording, samplerate)
                return str(audio_file)
            else:
                if not silent_mode:
                    print("🔇 No speech detected")
                return None
                
        except Exception as e:
            print(f"❌ Audio recording error: {e}")
            return None
        
    def transcribe(self, audio_file):
        """Convert speech to text using cached Whisper model"""
        if not audio_file or not os.path.exists(audio_file):
            return ""
            
        result = self.whisper_model.transcribe(audio_file)
        return result["text"].strip()
        
    def get_shell_command(self, query):
        """Get shell command from natural language"""
        try:
            # Try shell-genie first
            result = subprocess.run(
                ["shell-genie", "ask", query],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Fallback: basic command mapping
            return self.basic_command_mapping(query)
            
    def load_command_mappings(self):
        """Load command mappings from JSON file"""
        try:
            mappings_file = Path(__file__).parent / "command_mappings.json"
            with open(mappings_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load command mappings: {e}")
            return self.get_fallback_mappings()
            
    def get_fallback_mappings(self):
        """Fallback mappings if JSON file fails to load"""
        return {
            "file_operations": {
                "ls -la": ["list files", "show files"],
                "pwd": ["current directory", "where am i"]
            },
            "conversational": ["thinking", "hello", "thanks"]
        }
        
    def basic_command_mapping(self, query):
        """Advanced command mapping using external JSON file"""
        query_lower = query.lower().strip()
        
        # Clean up query by removing wake word references if present
        wake_phrases = self.config.get("wake_phrases", [])
        for wake_phrase in wake_phrases:
            if wake_phrase in query_lower:
                query_lower = query_lower.replace(wake_phrase, "").strip()
        
        # Remove common filler words
        filler_words = ["hey", "please", "can you", "could you", "would you"]
        for filler in filler_words:
            query_lower = query_lower.replace(filler, "").strip()
        
        # Load mappings if not already loaded
        if not hasattr(self, 'command_mappings'):
            self.command_mappings = self.load_command_mappings()
        
        # Check for conversational phrases first
        if query_lower in self.command_mappings.get("conversational", []):
            return "# CONVERSATIONAL"
            
        # Check all command categories
        for category, commands in self.command_mappings.items():
            if category == "conversational":
                continue
                
            for command, phrases in commands.items():
                for phrase in phrases:
                    if phrase.lower() in query_lower:
                        # Handle parameterized commands
                        if "{" in command:
                            return self.handle_parameterized_command(command, query_lower, phrase)
                        return command
                        
        return f"# Could not map: {query}"
        
    def handle_parameterized_command(self, command_template, query, matched_phrase):
        """Handle commands that need parameters like 'mkdir {name}'"""
        # Extract the parameter from the query
        query_words = query.replace(matched_phrase, "").strip().split()
        
        if "{name}" in command_template:
            if query_words:
                param = "_".join(query_words)  # Join words with underscore
                return command_template.replace("{name}", param)
            else:
                return command_template.replace("{name}", "new_item")
                
        elif "{file}" in command_template:
            if query_words:
                param = " ".join(query_words)
                return command_template.replace("{file}", param)
            else:
                return command_template.replace("{file}", "filename")
                
        return command_template
        
    def session_mode(self):
        """Active conversation session mode"""
        session_start = time.time()
        
        while self.session_active:
            try:
                # Listen for command with timeout prompting
                print("🎤 Listening for command...", end="", flush=True)
                command_audio = self.record_voice_activated(
                    silent_mode=True, 
                    timeout=self.command_wait_timeout
                )
                
                if not command_audio:
                    # No command detected, prompt user
                    print("\r🔔 I'm waiting for your command...")
                    self.speak("What's your command?")
                    
                    # Give another chance
                    command_audio = self.record_voice_activated(
                        silent_mode=True, 
                        timeout=self.command_wait_timeout
                    )
                    
                    if not command_audio:
                        print("⏰ Session timeout. Returning to wake word mode...")
                        self.speak("Going to sleep")
                        self.session_active = False
                        break
                
                # Transcribe command
                query = self.transcribe(command_audio)
                if not query:
                    print("\r❓ I didn't understand. Please try again...")
                    self.speak("Try again")
                    continue
                    
                print(f"\r📝 Command: {query}")
                
                # Check for session commands
                query_lower = query.lower().strip()
                if query_lower in ["exit", "quit", "stop", "goodbye", "sleep", "go to sleep"]:
                    self.speak("Going to sleep")
                    self.session_active = False
                    break
                elif query_lower in ["continue", "keep going", "stay active"]:
                    print("🔄 Staying active...")
                    continue
                    
                # Get shell command
                command = self.get_shell_command(query)
                
                # Check if it's a conversational phrase or unmappable command
                if command == "# CONVERSATIONAL":
                    print(f"💬 I heard: '{query}'")
                    responses = ["Got it", "I understand", "Okay", "Alright"]
                    import random
                    self.speak(random.choice(responses))
                    continue
                elif command.startswith("# Could not map:"):
                    print(f"❓ I'm not sure how to execute: '{query}'")
                    self.speak("I'm not sure how to do that. You can try: list files, current directory, show processes")
                    continue
                    
                print(f"💻 Suggested: {command}")
                
                # Auto-confirm with timeout
                if self.auto_confirm_with_timeout("Execute?"):
                    print("⚡ Executing command...")
                    
                    # Announce for longer commands
                    if any(cmd in command.lower() for cmd in ['find', 'grep', 'search', 'install', 'download']):
                        self.speak("Running command, this might take a moment")
                    
                    self.execute_command(command)
                    print("✅ Command completed")
                    # Only speak completion for long-running commands
                    if any(cmd in command.lower() for cmd in ['find', 'grep', 'search', 'install', 'download', 'git', 'npm']):
                        self.speak("Done")
                else:
                    print("❌ Command cancelled")
                
                # Check session timeout
                if time.time() - session_start > self.session_timeout:
                    print("\n⏰ Session timeout. Returning to wake word mode...")
                    self.speak("Going to sleep")
                    self.session_active = False
                    
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                # Don't speak errors to avoid feedback
                time.sleep(1)
                
    def run(self):
        """Main loop with wake word detection and session mode"""
        wake_name = self.config["wake_word_name"].title()
        self.clear_screen()
        self.speak(f"{wake_name} Voice Terminal Assistant ready")
        
        while True:
            try:
                if not self.session_active:
                    # Wake word mode
                    print("\n👂 Listening for wake word...", end="", flush=True)
                    
                    # Listen for wake word silently
                    audio_file = self.record_voice_activated(silent_mode=True)
                    if not audio_file:
                        continue
                        
                    # Transcribe wake word attempt
                    wake_text = self.transcribe(audio_file)
                    if not wake_text:
                        continue
                        
                    # Check for wake word first (don't print everything)
                    if not self.detect_wake_word(wake_text):
                        continue
                        
                    # Clear screen for new interaction
                    self.clear_screen()
                    print("\n✅ Wake word detected!")
                    self.speak(f"Hello! I'm listening. What can I do for you?")
                    
                    # Start session mode
                    self.session_active = True
                    
                # Run session mode
                if self.session_active:
                    self.session_mode()
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                time.sleep(2)
                
    def execute_command(self, command):
        """Execute shell command safely"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, 
                text=True, timeout=30
            )
            
            if result.stdout:
                print(result.stdout)
                # Only speak output for short results to avoid TTS feedback
                first_line = result.stdout.split('\n')[0].strip()
                if len(first_line) < 50:  # Only speak short outputs
                    self.speak(f"Output: {first_line}")
                
            if result.stderr:
                print(f"Error: {result.stderr}")
                # Don't speak errors to avoid feedback
                
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except Exception as e:
            print(f"Execution failed: {str(e)}")

if __name__ == "__main__":
    assistant = VoiceTerminal()
    assistant.run()