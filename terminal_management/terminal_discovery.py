"""
Terminal discovery service for finding and managing terminal windows.
"""

import time
import logging
from typing import List, Dict, Optional
from .terminal_models import TerminalWindow, TerminalInfo, TerminalStatus, TerminalApp
from .applescript_bridge import AppleScriptBridge

logger = logging.getLogger(__name__)

class TerminalDiscovery:
    """Service for discovering and tracking terminal windows"""
    
    def __init__(self):
        self.applescript = AppleScriptBridge()
        self.cached_terminals: Dict[str, TerminalInfo] = {}
        self.user_aliases: Dict[str, str] = {}  # alias -> terminal_id mapping
        self.last_discovery = 0
        self.discovery_interval = 5  # seconds
    
    def get_available_terminals(self, force_refresh: bool = False) -> List[TerminalInfo]:
        """Discover all available terminal windows"""
        current_time = time.time()
        
        # Use cache if recent and not forced
        if not force_refresh and (current_time - self.last_discovery) < self.discovery_interval:
            return list(self.cached_terminals.values())
        
        terminals = []
        
        # Discover Terminal.app windows
        try:
            terminal_windows = self.applescript.get_terminal_windows()
            for window in terminal_windows:
                # Check if we have user alias for this terminal
                if window.id in [t_id for alias, t_id in self.user_aliases.items()]:
                    for alias, t_id in self.user_aliases.items():
                        if t_id == window.id:
                            window.user_alias = alias
                            break
                
                terminal_info = TerminalInfo(
                    window=window,
                    status=TerminalStatus.AVAILABLE,  # Could be enhanced with actual status
                    last_command=None,
                    command_history=[],
                    response_time=None,
                    last_activity=None
                )
                terminals.append(terminal_info)
                
        except Exception as e:
            logger.error(f"Failed to discover Terminal.app windows: {e}")
        
        # Discover iTerm2 sessions
        try:
            iterm_sessions = self.applescript.get_iterm2_sessions()
            for session in iterm_sessions:
                # Check for user alias
                if session.id in [t_id for alias, t_id in self.user_aliases.items()]:
                    for alias, t_id in self.user_aliases.items():
                        if t_id == session.id:
                            session.user_alias = alias
                            break
                
                terminal_info = TerminalInfo(
                    window=session,
                    status=TerminalStatus.AVAILABLE,
                    last_command=None,
                    command_history=[],
                    response_time=None,
                    last_activity=None
                )
                terminals.append(terminal_info)
                
        except Exception as e:
            logger.error(f"Failed to discover iTerm2 sessions: {e}")
        
        # Discover Warp windows
        try:
            warp_windows = self.applescript.get_warp_windows()
            for window in warp_windows:
                # Check for user alias
                if window.id in [t_id for alias, t_id in self.user_aliases.items()]:
                    for alias, t_id in self.user_aliases.items():
                        if t_id == window.id:
                            window.user_alias = alias
                            break
                
                terminal_info = TerminalInfo(
                    window=window,
                    status=TerminalStatus.AVAILABLE,
                    last_command=None,
                    command_history=[],
                    response_time=None,
                    last_activity=None
                )
                terminals.append(terminal_info)
                
        except Exception as e:
            logger.error(f"Failed to discover Warp windows: {e}")

        # Add VS Code if running
        try:
            if self.applescript.is_application_running("Visual Studio Code"):
                vscode_terminal = TerminalWindow(
                    id="VSCode:integrated",
                    app_name="Visual Studio Code",
                    app_type=TerminalApp.VSCODE,
                    window_title="Integrated Terminal",
                    working_directory=None,
                    process_name=None,
                    user_alias=self.user_aliases.get("VSCode:integrated"),
                    is_active=False,
                    session_info={},
                    window_number=None
                )
                
                terminal_info = TerminalInfo(
                    window=vscode_terminal,
                    status=TerminalStatus.AVAILABLE,
                    last_command=None,
                    command_history=[],
                    response_time=None,
                    last_activity=None
                )
                terminals.append(terminal_info)
                
        except Exception as e:
            logger.error(f"Failed to check VS Code terminal: {e}")
        
        # Update cache
        self.cached_terminals = {info.window.id: info for info in terminals}
        self.last_discovery = current_time
        
        logger.info(f"Discovered {len(terminals)} terminal windows")
        return terminals
    
    def get_terminal_by_name(self, name: str) -> Optional[TerminalInfo]:
        """Find terminal by user-defined name, ID, or fuzzy match"""
        terminals = self.get_available_terminals()
        
        # Exact alias match
        if name.lower() in self.user_aliases:
            terminal_id = self.user_aliases[name.lower()]
            return self.cached_terminals.get(terminal_id)
        
        # Exact ID match
        for terminal in terminals:
            if terminal.window.id.lower() == name.lower():
                return terminal
        
        # Fuzzy matching on display names
        name_lower = name.lower()
        for terminal in terminals:
            display_name = terminal.window.display_name.lower()
            app_name = terminal.window.app_name.lower()
            
            # Check if name matches display name or app name
            if (name_lower in display_name or 
                name_lower in app_name or
                display_name.startswith(name_lower)):
                return terminal
        
        # Try window number matching for Terminal.app
        if name.lower().startswith("terminal") and name[-1].isdigit():
            window_num = int(name[-1])
            for terminal in terminals:
                if (terminal.window.app_type == TerminalApp.TERMINAL and 
                    terminal.window.window_number == window_num):
                    return terminal
        
        # Special cases
        if name.lower() in ["vscode", "vs code", "code"]:
            for terminal in terminals:
                if terminal.window.app_type == TerminalApp.VSCODE:
                    return terminal
        
        if name.lower() in ["iterm", "iterm2"]:
            for terminal in terminals:
                if terminal.window.app_type == TerminalApp.ITERM2:
                    return terminal
        
        if name.lower() in ["warp"]:
            for terminal in terminals:
                if terminal.window.app_type == TerminalApp.WARP:
                    return terminal
        
        return None
    
    def get_active_terminal(self) -> Optional[TerminalInfo]:
        """Get currently focused terminal"""
        try:
            active_window = self.applescript.get_active_terminal_window()
            if active_window:
                # Create TerminalInfo for active window
                return TerminalInfo(
                    window=active_window,
                    status=TerminalStatus.AVAILABLE,
                    last_command=None,
                    command_history=[],
                    response_time=None,
                    last_activity=None
                )
        except Exception as e:
            logger.error(f"Failed to get active terminal: {e}")
        
        return None
    
    def set_terminal_alias(self, terminal_id: str, alias: str) -> bool:
        """Set a user-defined alias for a terminal"""
        terminals = self.get_available_terminals()
        
        # Check if terminal exists
        terminal_exists = any(t.window.id == terminal_id for t in terminals)
        if not terminal_exists:
            return False
        
        # Remove old alias if it exists
        old_alias = None
        for existing_alias, existing_id in self.user_aliases.items():
            if existing_id == terminal_id:
                old_alias = existing_alias
                break
        
        if old_alias:
            del self.user_aliases[old_alias]
        
        # Set new alias
        self.user_aliases[alias.lower()] = terminal_id
        
        # Update cached terminal
        if terminal_id in self.cached_terminals:
            self.cached_terminals[terminal_id].window.user_alias = alias
        
        logger.info(f"Set alias '{alias}' for terminal {terminal_id}")
        return True
    
    def remove_terminal_alias(self, alias: str) -> bool:
        """Remove a terminal alias"""
        alias_lower = alias.lower()
        if alias_lower in self.user_aliases:
            terminal_id = self.user_aliases[alias_lower]
            del self.user_aliases[alias_lower]
            
            # Update cached terminal
            if terminal_id in self.cached_terminals:
                self.cached_terminals[terminal_id].window.user_alias = None
            
            logger.info(f"Removed alias '{alias}'")
            return True
        
        return False
    
    def get_terminal_aliases(self) -> Dict[str, str]:
        """Get all current terminal aliases"""
        return self.user_aliases.copy()
    
    def monitor_terminals(self) -> None:
        """Monitor terminal changes (could be used for background updates)"""
        # This could be enhanced to run in a background thread
        # and update the cache when terminals are created/destroyed
        pass
    
    def get_terminal_suggestions(self, query: str) -> List[TerminalInfo]:
        """Get terminal suggestions based on partial query"""
        terminals = self.get_available_terminals()
        suggestions = []
        
        query_lower = query.lower()
        
        for terminal in terminals:
            score = 0
            display_name = terminal.window.display_name.lower()
            app_name = terminal.window.app_name.lower()
            
            # Exact matches get highest score
            if query_lower == display_name or query_lower == app_name:
                score = 100
            # Starts with gets high score
            elif display_name.startswith(query_lower) or app_name.startswith(query_lower):
                score = 80
            # Contains gets medium score
            elif query_lower in display_name or query_lower in app_name:
                score = 60
            # Alias matches
            elif terminal.window.user_alias and query_lower in terminal.window.user_alias.lower():
                score = 90
            
            if score > 0:
                suggestions.append((terminal, score))
        
        # Sort by score and return terminals
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [terminal for terminal, _ in suggestions[:5]]  # Top 5 suggestions