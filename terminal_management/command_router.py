"""
Command router for directing voice commands to different terminals.
"""

import logging
from typing import Optional, Dict, Any
from .terminal_models import TerminalWindow, TerminalInfo, TerminalTarget, TerminalApp
from .terminal_discovery import TerminalDiscovery
from .applescript_bridge import AppleScriptBridge

logger = logging.getLogger(__name__)

class CommandRouter:
    """Routes voice commands to appropriate terminal windows"""
    
    def __init__(self, discovery: TerminalDiscovery):
        self.discovery = discovery
        self.applescript = AppleScriptBridge()
        self.current_target = "local"  # Default to local execution
        self.command_history: Dict[str, list] = {}  # terminal_id -> command history
    
    def set_target(self, target_name: str) -> bool:
        """Set the current command target"""
        if target_name.lower() in ["local", "current", "here"]:
            self.current_target = "local"
            return True
        
        # Check if target exists
        terminal = self.discovery.get_terminal_by_name(target_name)
        if terminal:
            self.current_target = terminal.window.id
            logger.info(f"Set target to: {terminal.window.display_name}")
            return True
        
        logger.warning(f"Target not found: {target_name}")
        return False
    
    def get_current_target(self) -> TerminalTarget:
        """Get the current command target"""
        if self.current_target == "local":
            return TerminalTarget("local")
        
        # Find the terminal window
        terminals = self.discovery.get_available_terminals()
        for terminal in terminals:
            if terminal.window.id == self.current_target:
                return TerminalTarget(self.current_target, terminal.window)
        
        # Target no longer exists, fallback to local
        logger.warning(f"Current target {self.current_target} no longer exists, falling back to local")
        self.current_target = "local"
        return TerminalTarget("local")
    
    def route_command(self, command: str, target: Optional[str] = None) -> tuple[bool, str]:
        """
        Route a command to the specified target or current target.
        Returns (success, message)
        """
        # Determine target
        if target:
            terminal = self.discovery.get_terminal_by_name(target)
            if not terminal:
                return False, f"Terminal '{target}' not found"
            target_window = terminal.window
        else:
            current_target = self.get_current_target()
            if current_target.is_local:
                return False, "Use local execution"  # Signal to caller to execute locally
            target_window = current_target.terminal_window
        
        # Validate target
        if not target_window:
            return False, "No valid target terminal"
        
        # Route based on application type
        success = False
        try:
            if target_window.app_type == TerminalApp.TERMINAL:
                success = self._send_to_terminal_app(target_window, command)
            elif target_window.app_type == TerminalApp.ITERM2:
                success = self._send_to_iterm2(target_window, command)
            elif target_window.app_type == TerminalApp.VSCODE:
                success = self._send_to_vscode(command)
            elif target_window.app_type == TerminalApp.WARP:
                success = self._send_to_warp(target_window, command)
            else:
                return False, f"Unsupported terminal type: {target_window.app_type}"
            
            if success:
                # Log command to history
                self._add_to_history(target_window.id, command)
                return True, f"Command sent to {target_window.display_name}"
            else:
                return False, f"Failed to send command to {target_window.display_name}"
                
        except Exception as e:
            logger.error(f"Error routing command: {e}")
            return False, f"Error sending command: {str(e)}"
    
    def _send_to_terminal_app(self, terminal: TerminalWindow, command: str) -> bool:
        """Send command to Terminal.app"""
        if terminal.window_number is None:
            logger.error("Terminal window number not available")
            return False
        
        return self.applescript.send_to_terminal_app(terminal.window_number, command)
    
    def _send_to_iterm2(self, terminal: TerminalWindow, command: str) -> bool:
        """Send command to iTerm2"""
        session_id = terminal.session_info.get("session_id")
        if not session_id:
            logger.error("iTerm2 session ID not available")
            return False
        
        return self.applescript.send_to_iterm2_session(session_id, command)
    
    def _send_to_vscode(self, command: str) -> bool:
        """Send command to VS Code integrated terminal"""
        return self.applescript.send_to_vscode(command)
    
    def _send_to_warp(self, terminal: TerminalWindow, command: str) -> bool:
        """Send command to Warp terminal"""
        window_number = terminal.session_info.get("window_number", 1)
        
        # Try UI scripting first (for existing windows)
        success = self.applescript.send_to_warp_via_ui_scripting(command, window_number)
        
        # If UI scripting fails, try launch configuration as fallback
        if not success:
            logger.warning("Warp UI scripting failed, trying launch configuration method")
            success = self.applescript.send_to_warp_via_launch_config(command, terminal.id)
        
        return success
    
    def _add_to_history(self, terminal_id: str, command: str) -> None:
        """Add command to terminal's history"""
        if terminal_id not in self.command_history:
            self.command_history[terminal_id] = []
        
        self.command_history[terminal_id].append(command)
        
        # Keep only last 50 commands
        if len(self.command_history[terminal_id]) > 50:
            self.command_history[terminal_id] = self.command_history[terminal_id][-50:]
    
    def get_command_history(self, terminal_id: str) -> list:
        """Get command history for a terminal"""
        return self.command_history.get(terminal_id, []).copy()
    
    def list_available_targets(self) -> list:
        """Get list of available command targets"""
        terminals = self.discovery.get_available_terminals()
        targets = ["local"]  # Always include local
        
        for terminal in terminals:
            targets.append(terminal.window.display_name)
        
        return targets
    
    def validate_command(self, command: str, terminal: TerminalWindow) -> tuple[bool, str]:
        """
        Validate command before execution.
        Returns (is_safe, warning_message)
        """
        # Check for destructive commands
        dangerous_patterns = [
            'rm -rf /',
            'sudo rm -rf',
            'format',
            'mkfs',
            '> /dev/sda',
            'dd if=',
            'chmod -R 777 /'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                return False, f"Dangerous command detected: {pattern}"
        
        # Check for remote session warnings
        if terminal.is_remote:
            remote_warning_patterns = [
                'rm -rf',
                'sudo',
                'chmod -R',
                'chown -R'
            ]
            
            for pattern in remote_warning_patterns:
                if pattern in command.lower():
                    return False, f"Potentially dangerous command on remote session: {pattern}"
        
        return True, ""
    
    def parse_contextual_command(self, query: str) -> tuple[Optional[str], str]:
        """
        Parse contextual commands like "In VS Code, run npm start"
        Returns (target, command) or (None, original_query)
        """
        query_lower = query.lower().strip()
        
        # Pattern: "in [target], [command]"
        if query_lower.startswith("in "):
            parts = query_lower.split(",", 1)
            if len(parts) == 2:
                target_part = parts[0][3:].strip()  # Remove "in "
                command_part = parts[1].strip()
                
                # Try to find the target
                terminal = self.discovery.get_terminal_by_name(target_part)
                if terminal:
                    return terminal.window.id, command_part
                
                # Try some common aliases
                target_aliases = {
                    "vs code": "VSCode:integrated",
                    "vscode": "VSCode:integrated", 
                    "code": "VSCode:integrated",
                    "terminal one": "Terminal:1",
                    "terminal 1": "Terminal:1",
                    "terminal two": "Terminal:2",
                    "terminal 2": "Terminal:2",
                    "iterm": "iTerm2",
                    "main session": "iTerm2",
                    "warp": "Warp:1",
                    "warp 1": "Warp:1",
                    "warp 2": "Warp:2",
                    "warp tab": "Warp:1",
                    "test tab": "Warp:1",
                    "test": "Warp:1"
                }
                
                if target_part in target_aliases:
                    return target_aliases[target_part], command_part
        
        # Pattern: "on [target], [command]"
        if query_lower.startswith("on "):
            parts = query_lower.split(",", 1)
            if len(parts) == 2:
                target_part = parts[0][3:].strip()  # Remove "on "
                command_part = parts[1].strip()
                
                terminal = self.discovery.get_terminal_by_name(target_part)
                if terminal:
                    return terminal.window.id, command_part
        
        return None, query
    
    def send_raw_text(self, text: str, target: Optional[str] = None) -> tuple[bool, str]:
        """
        Send raw text to terminal (not as a shell command).
        Automatically presses Enter after sending text.
        Returns (success, message)
        """
        # Determine target
        if target:
            terminal = self.discovery.get_terminal_by_name(target)
            if not terminal:
                return False, f"Terminal '{target}' not found"
            target_window = terminal.window
        else:
            current_target = self.get_current_target()
            if current_target.is_local:
                return False, "Cannot send raw text to local terminal"
            target_window = current_target.terminal_window
        
        # Validate target
        if not target_window:
            return False, "No valid target terminal"
        
        # Send text based on application type
        success = False
        try:
            if target_window.app_type == TerminalApp.TERMINAL:
                success = self._send_text_to_terminal_app(target_window, text)
            elif target_window.app_type == TerminalApp.ITERM2:
                success = self._send_text_to_iterm2(target_window, text)
            elif target_window.app_type == TerminalApp.VSCODE:
                success = self._send_text_to_vscode(text)
            elif target_window.app_type == TerminalApp.WARP:
                success = self._send_text_to_warp(target_window, text)
            else:
                return False, f"Unsupported terminal type: {target_window.app_type}"
            
            if success:
                # Log text to history
                self._add_to_history(target_window.id, f"[TEXT] {text}")
                return True, f"Text sent to {target_window.display_name}: '{text}'"
            else:
                return False, f"Failed to send text to {target_window.display_name}"
                
        except Exception as e:
            logger.error(f"Error sending text: {e}")
            return False, f"Error sending text: {str(e)}"
    
    def _send_text_to_terminal_app(self, terminal: TerminalWindow, text: str) -> bool:
        """Send raw text to Terminal.app"""
        if terminal.window_number is None:
            logger.error("Terminal window number not available")
            return False
        
        return self.applescript.send_text_to_terminal_app(terminal.window_number, text)
    
    def _send_text_to_iterm2(self, terminal: TerminalWindow, text: str) -> bool:
        """Send raw text to iTerm2"""
        session_id = terminal.session_info.get("session_id")
        if not session_id:
            logger.error("iTerm2 session ID not available")
            return False
        
        return self.applescript.send_text_to_iterm2_session(session_id, text)
    
    def _send_text_to_vscode(self, text: str) -> bool:
        """Send raw text to VS Code integrated terminal"""
        return self.applescript.send_text_to_vscode(text)
    
    def _send_text_to_warp(self, terminal: TerminalWindow, text: str) -> bool:
        """Send raw text to Warp terminal"""
        window_number = terminal.session_info.get("window_number", 1)
        return self.applescript.send_to_warp_via_ui_scripting(text, window_number)
    
    def get_target_status(self) -> Dict[str, Any]:
        """Get current routing status"""
        current_target = self.get_current_target()
        available_targets = self.list_available_targets()
        
        return {
            "current_target": str(current_target),
            "available_targets": available_targets,
            "total_terminals": len(available_targets) - 1,  # Exclude "local"
            "command_history_size": sum(len(hist) for hist in self.command_history.values())
        }