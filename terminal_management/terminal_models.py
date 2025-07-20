"""
Data models for terminal management system.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class TerminalStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    DISCONNECTED = "disconnected"
    UNKNOWN = "unknown"

class TerminalApp(Enum):
    TERMINAL = "Terminal"
    ITERM2 = "iTerm2"
    VSCODE = "Visual Studio Code"
    WARP = "Warp"
    ALACRITTY = "Alacritty"
    KITTY = "Kitty"
    HYPER = "Hyper"
    UNKNOWN = "Unknown"

@dataclass
class TerminalWindow:
    """Represents a terminal window/session"""
    id: str                           # Unique identifier
    app_name: str                     # Application name
    app_type: TerminalApp            # Application type enum
    window_title: str                # Window title text
    working_directory: Optional[str] # Current working directory
    process_name: Optional[str]      # Running process (zsh, bash, ssh, etc.)
    user_alias: Optional[str]        # Custom user-defined name
    is_active: bool                  # Currently focused
    session_info: Dict              # App-specific session data
    window_number: Optional[int]     # Window/tab number
    
    def __str__(self) -> str:
        alias = f" ({self.user_alias})" if self.user_alias else ""
        return f"{self.app_name} - {self.window_title}{alias}"
    
    @property
    def display_name(self) -> str:
        """Human-readable display name for voice interface"""
        if self.user_alias:
            return self.user_alias
        elif self.window_number:
            return f"{self.app_name} {self.window_number}"
        else:
            return f"{self.app_name} - {self.window_title[:30]}"
    
    @property
    def is_remote(self) -> bool:
        """Check if this is a remote session (SSH, etc.)"""
        if not self.process_name:
            return False
        return "ssh" in self.process_name.lower() or self.session_info.get("is_remote", False)

@dataclass
class TerminalInfo:
    """Extended information about a terminal window"""
    window: TerminalWindow
    status: TerminalStatus           # Current status
    last_command: Optional[str]      # Last executed command
    command_history: List[str]       # Recent command history
    response_time: Optional[float]   # Average response time
    last_activity: Optional[str]     # Last activity timestamp
    
    def __str__(self) -> str:
        status_icon = {
            TerminalStatus.AVAILABLE: "✅",
            TerminalStatus.BUSY: "⏳", 
            TerminalStatus.DISCONNECTED: "❌",
            TerminalStatus.UNKNOWN: "❓"
        }.get(self.status, "❓")
        
        return f"{status_icon} {self.window.display_name} - {self.status.value}"

class TerminalTarget:
    """Represents a command execution target"""
    
    def __init__(self, identifier: str, terminal_window: Optional[TerminalWindow] = None):
        self.identifier = identifier
        self.terminal_window = terminal_window
        self.is_local = identifier.lower() in ["local", "current", "here"]
    
    @property
    def is_valid(self) -> bool:
        """Check if target is valid for command execution"""
        return self.is_local or (self.terminal_window is not None)
    
    def __str__(self) -> str:
        if self.is_local:
            return "Local Terminal"
        elif self.terminal_window:
            return self.terminal_window.display_name
        else:
            return f"Unknown Target: {self.identifier}"