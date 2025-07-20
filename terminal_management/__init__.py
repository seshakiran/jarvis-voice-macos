"""
Terminal Management Package

Provides multi-terminal voice command routing capabilities for Jarvis Voice Assistant.
Enables sending voice commands to different terminal windows and applications.
"""

from .terminal_models import TerminalWindow, TerminalInfo
from .terminal_discovery import TerminalDiscovery
from .command_router import CommandRouter
from .applescript_bridge import AppleScriptBridge

__version__ = "1.0.0"
__all__ = [
    "TerminalWindow",
    "TerminalInfo", 
    "TerminalDiscovery",
    "CommandRouter",
    "AppleScriptBridge"
]