"""
AppleScript bridge for macOS terminal automation.
Provides native integration with Terminal.app, iTerm2, and VS Code.
"""

import subprocess
import json
import logging
from typing import List, Dict, Optional
from .terminal_models import TerminalWindow, TerminalApp

logger = logging.getLogger(__name__)

class AppleScriptBridge:
    """Bridge for executing AppleScript commands to control terminal applications"""
    
    def __init__(self):
        self.script_cache = {}
    
    def execute_script(self, script: str) -> Optional[str]:
        """Execute AppleScript and return result"""
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"AppleScript error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("AppleScript execution timed out")
            return None
        except Exception as e:
            logger.error(f"AppleScript execution failed: {e}")
            return None
    
    def get_terminal_windows(self) -> List[TerminalWindow]:
        """Discover all Terminal.app windows"""
        # Simplified approach to avoid AppleScript complexity
        script = '''
        tell application "Terminal"
            set windowCount to count of windows
            return windowCount as string
        end tell
        '''
        
        result = self.execute_script(script)
        if not result or not result.isdigit():
            return []
        
        window_count = int(result)
        windows = []
        
        # Get each window individually to avoid complex list handling
        for i in range(1, window_count + 1):
            window_script = f'''
            tell application "Terminal"
                try
                    set windowTitle to (get custom title of tab 1 of window {i})
                    return "{i}|" & windowTitle
                on error
                    return "{i}|Terminal Window {i}"
                end try
            end tell
            '''
            
            window_result = self.execute_script(window_script)
            if window_result and "|" in window_result:
                parts = window_result.split("|", 1)
                window_num = int(parts[0])
                title = parts[1] if len(parts) > 1 else f"Terminal Window {window_num}"
                
                window = TerminalWindow(
                    id=f"Terminal:{window_num}",
                    app_name="Terminal",
                    app_type=TerminalApp.TERMINAL,
                    window_title=title,
                    working_directory=None,
                    process_name=None,
                    user_alias=None,
                    is_active=False,
                    session_info={},
                    window_number=window_num
                )
                windows.append(window)
        
        return windows
    
    def get_iterm2_sessions(self) -> List[TerminalWindow]:
        """Discover all iTerm2 sessions"""
        # Check if iTerm2 is running first
        if not self.is_application_running("iTerm2"):
            return []
        
        # Simplified approach for iTerm2
        script = '''
        tell application "iTerm2"
            try
                tell current session of current tab of current window
                    set sessionId to unique id
                    set sessionName to name
                    return sessionId & "|" & sessionName
                end tell
            on error
                return ""
            end try
        end tell
        '''
        
        result = self.execute_script(script)
        if not result or "|" not in result:
            return []
        
        parts = result.split("|", 1)
        session_id = parts[0]
        name = parts[1] if len(parts) > 1 else "iTerm2 Session"
        
        window = TerminalWindow(
            id=f"iTerm2:{session_id}",
            app_name="iTerm2",
            app_type=TerminalApp.ITERM2,
            window_title=name,
            working_directory=None,
            process_name=None,
            user_alias=None,
            is_active=False,
            session_info={"session_id": session_id},
            window_number=None
        )
        
        return [window]
    
    def send_to_terminal_app(self, window_number: int, command: str) -> bool:
        """Send command to specific Terminal.app window"""
        script = f'''
        tell application "Terminal"
            try
                do script "{command}" in window {window_number}
                return "success"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
        '''
        
        result = self.execute_script(script)
        if result and result.startswith("success"):
            logger.info(f"Sent command to Terminal window {window_number}: {command}")
            return True
        else:
            logger.error(f"Failed to send command to Terminal: {result}")
            return False
    
    def send_to_iterm2_session(self, session_id: str, command: str) -> bool:
        """Send command to specific iTerm2 session"""
        script = f'''
        tell application "iTerm2"
            try
                tell session id "{session_id}"
                    write text "{command}"
                end tell
                return "success"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
        '''
        
        result = self.execute_script(script)
        if result and result.startswith("success"):
            logger.info(f"Sent command to iTerm2 session {session_id}: {command}")
            return True
        else:
            logger.error(f"Failed to send command to iTerm2: {result}")
            return False
    
    def send_to_vscode(self, command: str) -> bool:
        """Send command to VS Code integrated terminal"""
        # First, try to focus VS Code and open terminal
        focus_script = '''
        tell application "Visual Studio Code"
            activate
        end tell
        
        delay 0.5
        
        tell application "System Events"
            tell process "Code"
                keystroke "`" using {control down}
                delay 0.5
            end tell
        end tell
        '''
        
        # Then send the command
        command_script = f'''
        tell application "System Events"
            tell process "Code"
                keystroke "{command}"
                key code 36  -- Enter key
            end tell
        end tell
        '''
        
        # Execute focus script first
        if not self.execute_script(focus_script):
            logger.error("Failed to focus VS Code terminal")
            return False
        
        # Then send command
        result = self.execute_script(command_script)
        if result is not None:  # AppleScript may return empty string on success
            logger.info(f"Sent command to VS Code terminal: {command}")
            return True
        else:
            logger.error("Failed to send command to VS Code terminal")
            return False
    
    def is_application_running(self, app_name: str) -> bool:
        """Check if an application is currently running"""
        script = f'''
        tell application "System Events"
            return exists (processes where name is "{app_name}")
        end tell
        '''
        
        result = self.execute_script(script)
        return result == "true"
    
    def send_text_to_terminal_app(self, window_number: int, text: str) -> bool:
        """Send raw text to Terminal.app (with automatic Enter)"""
        # Escape quotes and special characters
        escaped_text = text.replace('"', '\\"').replace('\\', '\\\\')
        
        script = f'''
        tell application "Terminal"
            try
                tell window {window_number}
                    activate
                    delay 0.2
                    do script "{escaped_text}" in tab 1
                end tell
                return "success"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
        '''
        
        result = self.execute_script(script)
        if result and result.startswith("success"):
            logger.info(f"Sent text to Terminal window {window_number}: {text}")
            return True
        else:
            logger.error(f"Failed to send text to Terminal: {result}")
            return False
    
    def send_text_to_iterm2_session(self, session_id: str, text: str) -> bool:
        """Send raw text to iTerm2 (with automatic Enter)"""
        # Escape quotes and special characters
        escaped_text = text.replace('"', '\\"').replace('\\', '\\\\')
        
        script = f'''
        tell application "iTerm2"
            try
                tell session id "{session_id}"
                    write text "{escaped_text}"
                end tell
                return "success"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
        '''
        
        result = self.execute_script(script)
        if result and result.startswith("success"):
            logger.info(f"Sent text to iTerm2 session {session_id}: {text}")
            return True
        else:
            logger.error(f"Failed to send text to iTerm2: {result}")
            return False
    
    def send_text_to_vscode(self, text: str) -> bool:
        """Send raw text to VS Code terminal (with automatic Enter)"""
        # Escape quotes and special characters for AppleScript
        escaped_text = text.replace('"', '\\"').replace('\\', '\\\\')
        
        # First, ensure VS Code terminal is focused
        focus_script = '''
        tell application "Visual Studio Code"
            activate
        end tell
        
        delay 0.3
        
        tell application "System Events"
            tell process "Code"
                keystroke "`" using {control down}
                delay 0.3
            end tell
        end tell
        '''
        
        # Then send the text
        text_script = f'''
        tell application "System Events"
            tell process "Code"
                keystroke "{escaped_text}"
                key code 36  -- Enter key
            end tell
        end tell
        '''
        
        # Execute focus script first
        if not self.execute_script(focus_script):
            logger.error("Failed to focus VS Code terminal")
            return False
        
        # Then send text
        result = self.execute_script(text_script)
        if result is not None:  # AppleScript may return empty string on success
            logger.info(f"Sent text to VS Code terminal: {text}")
            return True
        else:
            logger.error("Failed to send text to VS Code terminal")
            return False
    
    def get_active_terminal_window(self) -> Optional[TerminalWindow]:
        """Get the currently active terminal window"""
        # Check Terminal.app first
        if self.is_application_running("Terminal"):
            script = '''
            tell application "Terminal"
                try
                    set frontWin to front window
                    set winIndex to 1
                    repeat with i from 1 to count of windows
                        if window i is frontWin then
                            set winIndex to i
                            exit repeat
                        end if
                    end repeat
                    
                    set title to (get custom title of tab 1 of window winIndex)
                    return winIndex & "|" & title
                on error
                    return ""
                end try
            end tell
            '''
            
            result = self.execute_script(script)
            if result and "|" in result:
                parts = result.split("|")
                window_num = int(parts[0])
                title = parts[1]
                
                return TerminalWindow(
                    id=f"Terminal:{window_num}",
                    app_name="Terminal",
                    app_type=TerminalApp.TERMINAL,
                    window_title=title,
                    working_directory=None,
                    process_name=None,
                    user_alias=None,
                    is_active=True,
                    session_info={},
                    window_number=window_num
                )
        
        # Check iTerm2 if Terminal.app not active
        if self.is_application_running("iTerm2"):
            script = '''
            tell application "iTerm2"
                try
                    tell current session of current tab of current window
                        set sessionId to unique id
                        set sessionName to name
                        return sessionId & "|" & sessionName
                    end tell
                on error
                    return ""
                end try
            end tell
            '''
            
            result = self.execute_script(script)
            if result and "|" in result:
                parts = result.split("|")
                session_id = parts[0]
                name = parts[1]
                
                return TerminalWindow(
                    id=f"iTerm2:{session_id}",
                    app_name="iTerm2",
                    app_type=TerminalApp.ITERM2,
                    window_title=name,
                    working_directory=None,
                    process_name=None,
                    user_alias=None,
                    is_active=True,
                    session_info={"session_id": session_id},
                    window_number=None
                )
        
        return None