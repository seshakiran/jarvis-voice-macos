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
import logging
from pathlib import Path

# Import terminal management
from terminal_management import TerminalDiscovery, CommandRouter

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
        
        # Terminal management (Phase 1)
        self.terminal_discovery = None
        self.command_router = None
        self.terminal_routing_enabled = self.config.get("terminal_routing", {}).get("enabled", False)
        
        if self.terminal_routing_enabled:
            try:
                self.terminal_discovery = TerminalDiscovery()
                self.command_router = CommandRouter(self.terminal_discovery)
                print("🔗 Terminal routing enabled")
            except Exception as e:
                print(f"⚠️  Terminal routing disabled due to error: {e}")
                self.terminal_routing_enabled = False
        
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
                
                # Handle terminal management commands first
                if self.terminal_routing_enabled and self.handle_terminal_management_command(query):
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
                
                # Security validation for terminal routing
                if self.terminal_routing_enabled and not self.validate_command_safety(command, query):
                    continue
                
                # Auto-confirm with timeout
                if self.auto_confirm_with_timeout("Execute?"):
                    print("⚡ Executing command...")
                    
                    # Announce for longer commands
                    if any(cmd in command.lower() for cmd in ['find', 'grep', 'search', 'install', 'download']):
                        self.speak("Running command, this might take a moment")
                    
                    # Check for contextual routing and execute appropriately
                    if self.terminal_routing_enabled:
                        success = self.execute_command_with_routing(command, query)
                    else:
                        success = self.execute_command(command)
                        
                    if success:
                        print("✅ Command completed")
                        # Only speak completion for long-running commands
                        if any(cmd in command.lower() for cmd in ['find', 'grep', 'search', 'install', 'download', 'git', 'npm']):
                            self.speak("Done")
                    else:
                        print("❌ Command execution failed")
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
        
        # Display startup status including terminal routing
        startup_message = f"{wake_name} Voice Terminal Assistant ready"
        if self.terminal_routing_enabled:
            startup_message += " with multi-terminal support"
            print("🔗 Multi-terminal routing enabled")
            # Show initial terminal discovery
            self.show_startup_terminals()
        else:
            print("📍 Local terminal mode")
            
        self.speak(startup_message)
        
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
                return False
                
            return True
                
        except subprocess.TimeoutExpired:
            print("Command timed out")
            return False
        except Exception as e:
            print(f"Execution failed: {str(e)}")
            return False
    
    def handle_terminal_management_command(self, query):
        """Handle terminal management specific commands"""
        query_lower = query.lower().strip()
        
        # Show available terminals
        if any(phrase in query_lower for phrase in ["show terminals", "list terminals", "available terminals", "what terminals"]):
            self.show_available_terminals()
            return True
            
        # Switch target terminal
        if any(phrase in query_lower for phrase in ["switch to", "use terminal", "send to", "target", "set target", "change to"]):
            target_name = self.extract_target_name(query_lower)
            if target_name:
                if self.command_router.set_target(target_name):
                    current_target = self.command_router.get_current_target()
                    self.speak(f"Now targeting {current_target}")
                    print(f"🎯 Target set to: {current_target}")
                else:
                    self.speak(f"Could not find terminal {target_name}")
                    print(f"❌ Terminal '{target_name}' not found")
            return True
            
        # Set terminal alias
        if any(phrase in query_lower for phrase in ["call this", "name this", "alias this", "set name"]):
            alias_name = self.extract_alias_name(query_lower)
            if alias_name:
                current_target = self.command_router.get_current_target()
                if not current_target.is_local and self.terminal_discovery.set_terminal_alias(current_target.identifier, alias_name):
                    self.speak(f"Named this terminal {alias_name}")
                    print(f"📛 Set alias '{alias_name}' for current terminal")
                else:
                    self.speak("Could not set alias")
                    print("❌ Failed to set terminal alias")
            return True
            
        # Show current target
        if any(phrase in query_lower for phrase in ["current target", "what target", "which terminal", "target status"]):
            current_target = self.command_router.get_current_target()
            self.speak(f"Current target is {current_target}")
            print(f"🎯 Current target: {current_target}")
            return True
        
        # Send arbitrary text to terminal
        if any(phrase in query_lower for phrase in ["send text", "type", "say", "send", "write", "input"]):
            self.handle_send_text_command(query_lower)
            return True
            
        # Send yes/no responses
        if any(phrase in query_lower for phrase in ["say yes", "say no", "answer yes", "answer no", "respond yes", "respond no"]):
            self.handle_response_command(query_lower)
            return True
            
        return False
    
    def show_available_terminals(self):
        """Display available terminals with voice feedback and interactive selection"""
        terminals = self.terminal_discovery.get_available_terminals(force_refresh=True)
        
        if not terminals:
            self.speak("No terminals found")
            print("❌ No terminals available")
            return
            
        print("\n📱 Available Terminals:")
        terminal_list = []
        
        # Add local option
        print(f"  0. 🏠 Local Terminal (current)")
        
        for i, terminal_info in enumerate(terminals, 1):
            terminal = terminal_info.window
            display_name = terminal.display_name
            status_icon = "✅" if terminal_info.status.value == "available" else "❌"
            working_dir = f" ({terminal.working_directory})" if terminal.working_directory else ""
            
            print(f"  {i}. {status_icon} {display_name}{working_dir}")
            terminal_list.append(terminal.display_name)
            
        # Show current target
        current_target = self.command_router.get_current_target()
        print(f"\n🎯 Current target: {current_target}")
        
        # Provide voice summary and offer selection
        if len(terminals) == 0:
            self.speak("Only local terminal available")
        elif len(terminals) == 1:
            self.speak(f"Found 1 terminal: {terminal_list[0]}. Say 'switch to' and a number or name to change target.")
        else:
            self.speak(f"Found {len(terminals)} terminals available. Say 'switch to' and a number or name to change target.")
        
        return terminals
    
    def extract_target_name(self, query):
        """Extract target terminal name from voice command"""
        # Remove command phrases to get the target name
        phrases_to_remove = ["switch to", "use terminal", "send to", "target", "set target", "change to", "use"]
        
        target_name = query
        for phrase in phrases_to_remove:
            if phrase in target_name:
                target_name = target_name.replace(phrase, "").strip()
        
        # Handle number references
        if target_name.isdigit():
            terminal_num = int(target_name)
            if terminal_num == 0:
                return "local"
            
            # Get terminals and find by number
            terminals = self.terminal_discovery.get_available_terminals()
            if terminal_num <= len(terminals):
                return terminals[terminal_num - 1].window.display_name
        
        # Handle word numbers
        number_words = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        
        for word, num in number_words.items():
            if word in target_name:
                if num == 0:
                    return "local"
                terminals = self.terminal_discovery.get_available_terminals()
                if num <= len(terminals):
                    return terminals[num - 1].window.display_name
        
        return target_name if target_name else None
    
    def show_startup_terminals(self):
        """Show discovered terminals at startup"""
        try:
            terminals = self.terminal_discovery.get_available_terminals(force_refresh=True)
            if terminals:
                print(f"📱 Discovered {len(terminals)} terminal(s):")
                for terminal_info in terminals:
                    terminal = terminal_info.window
                    status_icon = "✅" if terminal_info.status.value == "available" else "❌"
                    print(f"   {status_icon} {terminal.display_name}")
            else:
                print("📱 No external terminals found")
        except Exception as e:
            print(f"⚠️  Terminal discovery error: {e}")
    
    def handle_send_text_command(self, query):
        """Handle sending arbitrary text to terminals"""
        # Parse the command to extract target and text
        target_terminal, text_to_send = self.parse_send_text_command(query)
        
        if not text_to_send:
            self.speak("What text should I send?")
            print("❓ No text specified to send")
            return
        
        if target_terminal:
            # Send to specific terminal
            success, message = self.command_router.send_raw_text(text_to_send, target_terminal)
            if success:
                self.speak(f"Sent text to {target_terminal}")
                print(f"📤 {message}")
            else:
                self.speak("Failed to send text")
                print(f"❌ {message}")
        else:
            # Send to current target
            success, message = self.command_router.send_raw_text(text_to_send)
            if success:
                self.speak("Text sent")
                print(f"📤 {message}")
            else:
                self.speak("Failed to send text")
                print(f"❌ {message}")
    
    def handle_response_command(self, query):
        """Handle yes/no responses"""
        target_terminal = None
        response_text = "yes"
        
        # Extract target if specified
        if "to terminal" in query or "to " in query:
            target_terminal = self.extract_response_target(query)
        
        # Determine response
        if "no" in query:
            response_text = "no"
        
        if target_terminal:
            success, message = self.command_router.send_raw_text(response_text, target_terminal)
            if success:
                self.speak(f"Sent {response_text} to {target_terminal}")
                print(f"📤 {message}")
            else:
                self.speak("Failed to send response")
                print(f"❌ {message}")
        else:
            success, message = self.command_router.send_raw_text(response_text)
            if success:
                self.speak(f"Sent {response_text}")
                print(f"📤 {message}")
            else:
                self.speak("Failed to send response")
                print(f"❌ {message}")
    
    def parse_send_text_command(self, query):
        """Parse send text command to extract target and text"""
        # Patterns: "send text hello to terminal 1", "type hello", "say hello to vs code"
        
        # Remove command phrases
        text_query = query
        for phrase in ["send text", "type", "say", "send", "write", "input"]:
            if phrase in text_query:
                text_query = text_query.replace(phrase, "").strip()
                break
        
        # Check for target specification
        target_terminal = None
        text_to_send = text_query
        
        if " to terminal" in text_query or " to " in text_query:
            parts = text_query.split(" to ", 1)
            if len(parts) == 2:
                text_to_send = parts[0].strip()
                target_part = parts[1].strip()
                
                # Clean up target part
                target_part = target_part.replace("terminal ", "").strip()
                target_terminal = target_part
        
        return target_terminal, text_to_send
    
    def extract_response_target(self, query):
        """Extract target terminal from response command"""
        if " to terminal " in query:
            parts = query.split(" to terminal ", 1)
            if len(parts) == 2:
                return parts[1].strip()
        elif " to " in query:
            parts = query.split(" to ", 1)
            if len(parts) == 2:
                target = parts[1].strip()
                # Remove common words
                target = target.replace("terminal ", "").strip()
                return target
        return None
    
    def extract_alias_name(self, query):
        """Extract alias name from voice command"""
        phrases_to_remove = ["call this", "name this", "alias this", "set name", "to"]
        
        for phrase in phrases_to_remove:
            if phrase in query:
                return query.replace(phrase, "").strip()
        
        return None
    
    def validate_command_safety(self, command, original_query):
        """Validate command safety with user confirmation for dangerous operations"""
        if not self.command_router:
            return True
        
        # Determine target terminal
        target, parsed_command = self.command_router.parse_contextual_command(original_query)
        if target:
            terminal = self.terminal_discovery.get_terminal_by_name(target)
            if terminal:
                target_window = terminal.window
            else:
                return True  # If target not found, let the router handle it
        else:
            current_target = self.command_router.get_current_target()
            if current_target.is_local:
                return True  # Local execution, no special validation
            target_window = current_target.terminal_window
        
        if not target_window:
            return True
        
        # Validate the command
        is_safe, warning = self.command_router.validate_command(command, target_window)
        
        if not is_safe:
            print(f"⚠️  Security Warning: {warning}")
            self.speak("Security warning detected")
            
            if target_window.is_remote:
                self.speak("This command will run on a remote session. Are you sure?")
                confirm_msg = f"⚠️  Execute potentially dangerous command on remote session?"
            else:
                self.speak("This command could be dangerous. Are you sure?")
                confirm_msg = f"⚠️  Execute potentially dangerous command?"
            
            # Require explicit confirmation (no timeout)
            confirmed = self.get_explicit_confirmation(confirm_msg)
            if not confirmed:
                print("❌ Command cancelled for safety")
                self.speak("Command cancelled for safety")
                return False
            else:
                print("⚠️  User confirmed dangerous command")
                self.speak("Proceeding with caution")
        
        return True
    
    def get_explicit_confirmation(self, prompt):
        """Get explicit user confirmation without timeout"""
        print(f"{prompt} [y/N]: ", end="", flush=True)
        try:
            user_input = input().lower().strip()
            return user_input in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return False
    
    def execute_command_with_routing(self, command, original_query):
        """Execute command with terminal routing support"""
        if not self.command_router:
            return self.execute_command(command)
        
        # Check for contextual routing in original query
        target, parsed_command = self.command_router.parse_contextual_command(original_query)
        
        if target:
            # Contextual command detected
            success, message = self.command_router.route_command(parsed_command, target)
            if success:
                print(f"📤 {message}")
                return True
            elif "Use local execution" in message:
                # Fallback to local execution
                return self.execute_command(command)
            else:
                print(f"❌ {message}")
                return False
        else:
            # Use current target
            success, message = self.command_router.route_command(command)
            if success:
                print(f"📤 {message}")
                return True
            elif "Use local execution" in message:
                # Fallback to local execution
                return self.execute_command(command)
            else:
                print(f"❌ {message}")
                return False

if __name__ == "__main__":
    assistant = VoiceTerminal()
    assistant.run()