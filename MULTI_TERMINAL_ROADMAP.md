# 🎯 Multi-Terminal Voice Command Routing - Implementation Roadmap

## 📋 Overview
This document outlines the plan to extend Jarvis Voice Terminal Assistant to send voice commands to different terminal windows and applications, enabling users to control multiple terminals, IDEs, and command-line tools from a single voice interface.

## 🎯 Goals
- Send voice commands to any terminal window/application
- Provide intuitive terminal selection and targeting
- Support popular terminal apps (Terminal.app, iTerm2, VS Code)
- Maintain security and reliability
- Seamless user experience with voice-based control

## 🔧 Technical Approaches (macOS)

### Method 1: AppleScript Automation (Primary)
```applescript
tell application "Terminal"
    do script "ls -la" in window 1
end tell

tell application "iTerm2"
    tell current session of current tab of current window
        write text "npm start"
    end tell
end tell
```
**Pros:** Native macOS integration, reliable, app-specific control  
**Cons:** Limited to AppleScript-compatible applications

### Method 2: System Events + Window Management
```applescript
tell application "System Events"
    tell process "Terminal"
        set frontmost to true
        keystroke "ls -la"
        key code 36  # Enter key
    end tell
end tell
```
**Pros:** Universal compatibility, works with any application  
**Cons:** Requires focus management, potential reliability issues

### Method 3: tmux Session Management
```bash
tmux send-keys -t session:window "ls -la" Enter
tmux new-session -d -s "voice-session"
```
**Pros:** Powerful session control, remote compatibility  
**Cons:** Requires tmux setup, additional complexity

## 🎨 User Interface Design

### Window Selection Methods

#### 1. Interactive Voice Menu
```
🎤 Jarvis: "Available terminals:"
   1. Terminal - Window 1 (~/projects)
   2. iTerm2 - Main Session (ssh://server.com) 
   3. VS Code - Integrated Terminal (React App)
   4. Terminal - Window 2 (~/downloads)

🎤 Jarvis: "Say number or name to select target."
User: "Terminal one"
🎤 Jarvis: "Now targeting Terminal Window 1"
```

#### 2. Direct Voice Commands
```
"Send to terminal one"           → Target Terminal.app window 1
"Use iTerm main session"         → Target iTerm2 main session  
"Switch to VS Code terminal"     → Target VS Code integrated terminal
"Target SSH session"             → Target SSH connection window
```

#### 3. Contextual Command Routing
```
"In VS Code, run npm start"      → Send "npm start" to VS Code terminal
"In terminal two, list files"    → Send "ls -la" to Terminal window 2
"On server, check disk space"    → Send "df -h" to SSH session
"In dev environment, git status" → Send to named terminal alias
```

### Terminal Identification
- **Window Title**: Extract meaningful names from window titles
- **Process Info**: Identify running processes and working directories
- **User Aliases**: Allow custom naming for frequently used terminals
- **Application Type**: Distinguish between Terminal.app, iTerm2, VS Code, etc.

## 🏗️ Architecture Design

### Core Components

#### 1. Terminal Discovery Service
```python
class TerminalDiscovery:
    def get_available_terminals(self) -> List[TerminalWindow]:
        """Discover all available terminal windows"""
        
    def get_terminal_by_name(self, name: str) -> Optional[TerminalWindow]:
        """Find terminal by user-defined name or identifier"""
        
    def get_active_terminal(self) -> TerminalWindow:
        """Get currently focused terminal"""
        
    def monitor_terminals(self) -> None:
        """Monitor for new/closed terminal windows"""
```

#### 2. Command Router
```python
class CommandRouter:
    def __init__(self, discovery: TerminalDiscovery):
        self.current_target = "local"
        
    def send_to_terminal(self, terminal_id: str, command: str) -> bool:
        """Send command to specific terminal"""
        
    def send_to_active(self, command: str) -> bool:
        """Send to currently active terminal"""
        
    def execute_locally(self, command: str) -> bool:
        """Execute in current process (existing behavior)"""
        
    def set_default_target(self, target: str) -> None:
        """Set default target for commands"""
```

#### 3. Window Manager
```python
class WindowManager:
    def list_terminals(self) -> List[TerminalInfo]:
        """Get list of all terminal windows with metadata"""
        
    def focus_terminal(self, terminal_id: str) -> bool:
        """Bring terminal window to focus"""
        
    def send_keystrokes(self, terminal_id: str, text: str) -> bool:
        """Send text input to specific terminal"""
        
    def get_window_info(self, terminal_id: str) -> TerminalInfo:
        """Get detailed info about specific terminal"""
```

#### 4. AppleScript Bridge
```python
class AppleScriptBridge:
    def execute_script(self, script: str) -> str:
        """Execute AppleScript and return result"""
        
    def send_to_terminal_app(self, window_id: int, command: str) -> bool:
        """Send command to Terminal.app window"""
        
    def send_to_iterm2(self, session_id: str, command: str) -> bool:
        """Send command to iTerm2 session"""
        
    def send_to_vscode(self, command: str) -> bool:
        """Send command to VS Code integrated terminal"""
```

### Data Models

#### TerminalWindow
```python
@dataclass
class TerminalWindow:
    id: str                    # Unique identifier
    app_name: str             # "Terminal", "iTerm2", "VS Code"
    window_title: str         # Window title text
    working_directory: str    # Current working directory
    process_name: str         # Running process (zsh, bash, ssh, etc.)
    user_alias: Optional[str] # Custom user-defined name
    is_active: bool          # Currently focused
    session_info: Dict       # App-specific session data
```

#### TerminalInfo
```python
@dataclass  
class TerminalInfo:
    window: TerminalWindow
    status: str              # "available", "busy", "disconnected"
    last_command: str        # Last executed command
    command_history: List[str] # Recent command history
```

## ⚙️ Configuration Extension

### Enhanced Config Schema
```json
{
  "wake_word_name": "jarvis",
  "confirmation_timeout": 2,
  "terminal_routing": {
    "enabled": true,
    "default_target": "local",
    "auto_discover": true,
    "discovery_interval": 5,
    "preferred_apps": ["Terminal", "iTerm2", "VS Code"],
    "confirmation_required": {
      "destructive_commands": true,
      "remote_sessions": true,
      "new_terminals": false
    },
    "named_terminals": {
      "dev": "iTerm2:Session-1",
      "server": "Terminal:SSH-prod",
      "local": "current",
      "react": "VS Code:Terminal"
    },
    "app_preferences": {
      "Terminal": {
        "method": "applescript",
        "focus_before_send": true
      },
      "iTerm2": {
        "method": "applescript", 
        "session_detection": true
      },
      "VS Code": {
        "method": "applescript",
        "terminal_panel": "integrated"
      }
    }
  }
}
```

## 🎙️ Voice Command Extensions

### New Command Categories

#### Terminal Management Commands
```json
{
  "terminal_control": {
    "list_terminals": [
      "show terminals", "available terminals", "list windows",
      "what terminals", "terminal list"
    ],
    "switch_target": [
      "switch to", "use terminal", "send to", "target",
      "set target", "change to"
    ],
    "focus_terminal": [
      "focus on", "bring to front", "show terminal",
      "go to terminal"
    ],
    "name_terminal": [
      "call this", "name this terminal", "alias this",
      "set name to"
    ]
  }
}
```

#### Contextual Routing Commands
```json
{
  "contextual_routing": {
    "in_terminal": [
      "in terminal", "in window", "on terminal"
    ],
    "in_app": [
      "in VS Code", "in iTerm", "in terminal app"
    ],
    "in_session": [
      "in session", "in SSH", "on server"
    ]
  }
}
```

### Enhanced Natural Language Processing

#### Context Detection Patterns
```python
# Parse contextual commands
"In VS Code, run npm start"
→ target: "VS Code", command: "npm start"

"In terminal two, list files" 
→ target: "Terminal:2", command: "ls -la"

"On server, check disk space"
→ target: "SSH-session", command: "df -h"
```

#### Smart Target Resolution
```python
# Fuzzy matching for terminal selection
"terminal one" → "Terminal:Window-1"
"main session" → "iTerm2:Main-Session"  
"VS Code" → "VS Code:Integrated-Terminal"
"dev environment" → User-defined alias
```

## 🔄 Implementation Phases

### Phase 1: Foundation & Discovery (Week 1)
**Goal:** Basic terminal discovery and AppleScript integration

**Tasks:**
- [ ] Create `terminal_discovery.py` with basic window enumeration
- [ ] Implement `applescript_bridge.py` for Terminal.app and iTerm2
- [ ] Add terminal discovery to main voice loop
- [ ] Basic "show terminals" voice command
- [ ] Configuration structure for terminal routing

**Deliverables:**
- Voice command: "Show available terminals"
- Basic AppleScript execution for sending commands
- Terminal window discovery and listing

### Phase 2: Command Routing (Week 2)  
**Goal:** Send commands to selected terminals

**Tasks:**
- [ ] Create `command_router.py` with target management
- [ ] Implement terminal targeting voice commands
- [ ] Add confirmation prompts for remote execution
- [ ] Integration with existing command mapping system
- [ ] Error handling and fallback mechanisms

**Deliverables:**
- Voice commands: "Send to terminal one", "Use iTerm session"
- Reliable command execution in target terminals
- Smart fallback to local execution

### Phase 3: User Experience (Week 3)
**Goal:** Intuitive terminal selection and management

**Tasks:**
- [ ] Interactive terminal selection menu
- [ ] Named terminal aliases and persistence
- [ ] Contextual command parsing ("In VS Code, run...")
- [ ] Terminal status monitoring and updates
- [ ] Enhanced voice feedback and confirmations

**Deliverables:**
- Natural contextual commands
- Persistent terminal naming and preferences
- Improved user experience flow

### Phase 4: Advanced Features (Week 4)
**Goal:** Production-ready advanced functionality

**Tasks:**
- [ ] VS Code integrated terminal support
- [ ] SSH session detection and management
- [ ] tmux integration for power users
- [ ] Command history per terminal
- [ ] Security enhancements and validation

**Deliverables:**
- Full IDE integration
- Remote session management
- Enterprise-ready security features

## 🎯 User Experience Flows

### Initial Setup Flow
```
1. User: "Hey Jarvis"
2. Jarvis: "Hello! I can now control multiple terminals."
3. User: "Show available terminals"
4. Jarvis: "Found 3 terminals: Terminal Window 1, iTerm Main, VS Code Terminal"
5. User: "Call VS Code terminal 'React App'"
6. Jarvis: "VS Code terminal is now named 'React App'"
7. User: "Set default target to React App"
8. Jarvis: "Default target set to React App"
```

### Daily Usage Flow
```
1. User: "Hey Jarvis"
2. Jarvis: "Hello! Current target: React App"
3. User: "In terminal one, check git status"
4. Jarvis: "Sending 'git status' to Terminal Window 1"
   → Command executes in Terminal.app
5. User: "Switch to React App"
6. Jarvis: "Now targeting React App terminal"
7. User: "Run npm start"
8. Jarvis: "Sending 'npm start' to React App"
   → Command executes in VS Code terminal
```

### Advanced Workflow
```
1. User: "Show terminals"
2. Jarvis: "Available: Local (current), Dev Server (SSH), React App, Database"
3. User: "In Dev Server, check logs"
4. Jarvis: "Sending 'tail -f /var/log/app.log' to Dev Server"
5. User: "In Database terminal, show tables"  
6. Jarvis: "Sending 'SHOW TABLES;' to Database terminal"
7. User: "Back to local"
8. Jarvis: "Now targeting local terminal"
```

## ⚙️ Technical Implementation Details

### AppleScript Templates

#### Terminal.app Integration
```applescript
-- List Terminal windows
tell application "Terminal"
    set windowList to {}
    repeat with i from 1 to count of windows
        set windowInfo to "Window " & i & ": " & (get custom title of tab 1 of window i)
        set end of windowList to windowInfo
    end repeat
    return windowList
end tell

-- Send command to specific Terminal window
tell application "Terminal"
    do script "ls -la" in window 1
end tell
```

#### iTerm2 Integration
```applescript
-- List iTerm2 sessions
tell application "iTerm2"
    set sessionList to {}
    repeat with theTab in tabs of current window
        repeat with theSession in sessions of theTab
            set sessionInfo to (get name of theSession)
            set end of sessionList to sessionInfo
        end repeat
    end repeat
    return sessionList
end tell

-- Send command to iTerm2 session
tell application "iTerm2"
    tell current session of current tab of current window
        write text "npm start"
    end tell
end tell
```

#### VS Code Integration
```applescript
-- Send to VS Code integrated terminal
tell application "Visual Studio Code"
    activate
end tell

tell application "System Events"
    tell process "Code"
        -- Focus terminal panel
        keystroke "t" using {control down, shift down}
        delay 0.5
        -- Send command
        keystroke "npm start"
        key code 36  -- Enter
    end tell
end tell
```

### Error Handling Strategies

#### Terminal Availability
```python
def send_command_safely(self, target: str, command: str) -> bool:
    try:
        terminal = self.discovery.get_terminal_by_name(target)
        if not terminal:
            self.speak(f"Terminal {target} not found. Using local terminal.")
            return self.execute_locally(command)
            
        if not self.window_manager.is_responsive(terminal.id):
            self.speak(f"Terminal {target} not responding. Using local terminal.")
            return self.execute_locally(command)
            
        return self.window_manager.send_command(terminal.id, command)
        
    except Exception as e:
        self.speak("Terminal error. Executing locally.")
        return self.execute_locally(command)
```

#### Command Validation
```python
def validate_command(self, command: str, terminal: TerminalWindow) -> bool:
    # Check for destructive commands
    dangerous_patterns = ['rm -rf', 'sudo rm', '> /dev/', 'format', 'mkfs']
    if any(pattern in command.lower() for pattern in dangerous_patterns):
        if terminal.session_info.get('is_remote'):
            return self.confirm_dangerous_command(command, terminal)
    
    # Check for remote session commands
    if terminal.session_info.get('is_ssh'):
        return self.confirm_remote_command(command, terminal)
        
    return True
```

## 🛡️ Security & Safety Considerations

### Command Validation
- **Destructive Command Detection**: Identify and confirm dangerous operations
- **Remote Session Warnings**: Extra confirmation for SSH/remote commands  
- **Command History**: Log all commands sent to external terminals
- **Escape Sequences**: Sanitize input to prevent terminal injection

### Access Control
- **Application Permissions**: Request necessary macOS accessibility permissions
- **Terminal Whitelisting**: Only interact with approved terminal applications
- **User Confirmation**: Configurable confirmation levels for different command types
- **Session Validation**: Verify terminal sessions before sending commands

### Privacy & Data Protection
- **Local Processing**: All voice processing remains local (no cloud)
- **Command Logging**: Optional command history with user control
- **Session Isolation**: Prevent command leakage between different terminals
- **Credential Protection**: Avoid logging or exposing sensitive information

## 📊 Performance Considerations

### Optimization Strategies
- **Terminal Discovery Caching**: Cache terminal information to reduce API calls
- **Efficient AppleScript**: Minimize AppleScript execution overhead
- **Lazy Loading**: Only discover terminals when needed
- **Background Monitoring**: Efficiently monitor terminal changes

### Resource Management
- **Memory Usage**: Efficient data structures for terminal tracking
- **CPU Usage**: Optimize voice processing and command routing
- **Battery Impact**: Minimize background activity on laptops
- **Network Usage**: No additional network requirements

## 🔮 Future Enhancements

### Advanced Features
- **Remote Terminal Support**: SSH/cloud terminal integration
- **Terminal Multiplexing**: Advanced tmux/screen session management
- **IDE Plugins**: Deep integration with development environments
- **Team Collaboration**: Share terminal sessions via voice commands

### AI Enhancements
- **Smart Context Switching**: Automatically select appropriate terminals
- **Command Suggestion**: Suggest relevant commands based on terminal context
- **Workflow Learning**: Learn user patterns for intelligent defaults
- **Natural Language Enhancement**: More sophisticated command interpretation

### Platform Expansion
- **Linux Support**: Extend to Linux desktop environments
- **Windows Support**: Windows Terminal and PowerShell integration
- **Cross-Platform**: Unified experience across operating systems
- **Mobile Companion**: iOS/Android companion apps

## 📝 File Structure Changes

### New Files
```
voice-terminal-macos/
├── terminal_management/
│   ├── __init__.py
│   ├── terminal_discovery.py      # Core discovery service
│   ├── command_router.py          # Command routing logic
│   ├── window_manager.py          # Window management utilities
│   ├── applescript_bridge.py      # AppleScript integration
│   └── terminal_models.py         # Data models and types
├── scripts/
│   ├── terminal_app.applescript   # Terminal.app automation
│   ├── iterm2.applescript         # iTerm2 automation
│   └── vscode.applescript         # VS Code automation
└── tests/
    ├── test_terminal_discovery.py
    ├── test_command_router.py
    └── test_applescript_bridge.py
```

### Modified Files
```
├── voice_exec_macos.py           # Add terminal routing integration
├── command_mappings.json         # Add terminal management commands  
├── setup_config.py               # Add terminal routing configuration
├── config_manager.py             # Add terminal settings management
└── README.md                     # Update with multi-terminal features
```

## 🎉 Success Metrics

### Functionality Goals
- [ ] Successfully discover and list terminal windows
- [ ] Send commands to 3+ different terminal applications
- [ ] Support named terminal aliases and persistence
- [ ] Handle contextual commands ("In VS Code, run...")
- [ ] Provide reliable fallback to local execution

### User Experience Goals  
- [ ] Intuitive voice commands for terminal selection
- [ ] < 2 second response time for command routing
- [ ] Clear feedback on target terminal changes
- [ ] Minimal setup required for basic functionality
- [ ] Comprehensive error handling and recovery

### Technical Goals
- [ ] 99%+ command delivery success rate
- [ ] Graceful handling of terminal disconnections
- [ ] Efficient resource usage (< 50MB additional memory)
- [ ] Clean integration with existing voice assistant
- [ ] Comprehensive test coverage (> 80%)

---

## 🚀 Getting Started

Once implementation begins, users will be able to:

1. **Install the enhanced version**
   ```bash
   git pull origin main
   ./setup_macos.sh  # Updates with new dependencies
   ```

2. **Enable multi-terminal features**
   ```bash
   python3 config_manager.py
   # Select "Enable terminal routing" option
   ```

3. **Start using multi-terminal voice commands**
   ```bash
   ./run.sh
   # Say: "Hey Jarvis, show available terminals"
   ```

This roadmap provides a comprehensive foundation for implementing multi-terminal voice command routing while maintaining the existing functionality and user experience of Jarvis Voice Terminal Assistant.

---

**Implementation Timeline: 4 weeks**  
**Estimated Effort: 40-60 hours**  
**Dependencies: macOS accessibility permissions, AppleScript support**