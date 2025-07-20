# 🎙️ Voice Terminal Assistant - Multi-Terminal Usage Guide

## Quick Start

1. **Initial Setup**:
   ```bash
   python3 setup_config.py
   # Say "y" when asked about multi-terminal support
   ```

2. **Run the Assistant**:
   ```bash
   python3 voice_exec_macos.py
   ```

3. **Wake up the assistant**:
   Say: "Hey Jarvis" (or whatever name you chose)

## 🖥️ Multi-Terminal Commands

### Terminal Management
- **"show terminals"** - Lists all available terminals
- **"switch to terminal 1"** - Target specific terminal by number  
- **"switch to VS Code"** - Target terminal by name
- **"current target"** - Show which terminal is currently targeted

### Send Text to Terminals

#### Send Any Text (Auto-presses Enter):
- **"send text hello world"** - Send "hello world" to current target
- **"type go do this to terminal 1"** - Send "go do this" to terminal 1
- **"say yes to VS Code"** - Send "yes" to VS Code terminal

#### Quick Responses:
- **"say yes"** - Send "yes" to current target terminal
- **"say no to terminal 2"** - Send "no" to terminal 2
- **"answer yes to iTerm"** - Send "yes" to iTerm

#### Contextual Commands:
- **"in terminal 1, send hello"** - Send "hello" to terminal 1
- **"in VS Code, type npm start"** - Send "npm start" to VS Code

## 📝 Examples

### Scenario 1: Responding to Prompts
```
Terminal shows: "Do you want to continue? (y/n)"
You say: "say yes to terminal 1"
Result: "yes" + Enter is sent to terminal 1
```

### Scenario 2: Sending Commands
```
You say: "send git status to terminal 2"  
Result: "git status" + Enter is sent to terminal 2
```

### Scenario 3: Interactive Setup
```
You say: "show terminals"
Assistant: "Found 3 terminals: Terminal 1, iTerm2, VS Code"
You say: "switch to terminal 2"
You say: "type ./install.sh"
Result: "./install.sh" + Enter is sent to terminal 2
```

## 🎯 Terminal Targeting

### By Number:
- "terminal 1", "terminal 2", etc.
- "one", "two", "three" (spoken numbers)

### By Name:
- "VS Code", "iTerm", "Terminal"
- Custom aliases you set

### Setting Aliases:
- Say "call this React App" while targeting a terminal
- Then use "switch to React App"

## ⚡ Features

- ✅ **Automatic Enter**: All text is sent with Enter automatically
- ✅ **Any Text**: Send non-command text like "yes", "no", "go do this"
- ✅ **Multiple Terminals**: Terminal.app, iTerm2, VS Code support
- ✅ **Voice Targeting**: Specify which terminal by voice
- ✅ **Safety**: Validation for dangerous commands
- ✅ **Aliases**: Custom names for frequently used terminals

## 🔧 Supported Terminal Apps

1. **Terminal.app** - macOS built-in terminal
2. **iTerm2** - Popular third-party terminal
3. **VS Code** - Integrated terminal in Visual Studio Code

The assistant automatically discovers running terminals and lets you target them by voice!