# Warp Terminal Integration Guide

## Overview

This voice terminal system now supports Warp terminal, though with some limitations due to Warp's lack of native AppleScript support. Here's how to use it effectively:

## How Warp Integration Works

### 1. **Window/Tab Detection**
- The system detects if Warp is running and creates generic window representations
- Windows are identified as `Warp:1`, `Warp:2`, etc.
- Due to Warp's limitations, we can't get detailed tab information

### 2. **Command Delivery Methods**

#### **Method A: UI Scripting (Primary)**
- Uses AppleScript to simulate keyboard input
- Works with existing Warp windows/tabs
- More reliable for sending commands to active windows

#### **Method B: Launch Configuration (Fallback)**
- Creates temporary YAML configuration files
- Opens new Warp tabs with pre-configured commands
- Used when UI scripting fails

## Voice Commands for Warp

### **Basic Usage**
```
"Hey Jarvis"
"Switch to Warp"               # Targets any Warp window
"List files"                   # Sends 'ls' to current Warp window
"Check disk space"             # Sends 'df -h' to Warp
```

### **Specific Window Targeting**
```
"Switch to Warp 1"             # Target specific Warp window
"In Warp, run npm start"       # Contextual command
"Use Warp 2"                   # Switch to second Warp window
```

### **Setting Custom Aliases**
You can create custom names for your Warp windows:
```python
# In the voice terminal system
discovery = TerminalDiscovery()
discovery.set_terminal_alias("Warp:1", "frontend")
discovery.set_terminal_alias("Warp:2", "backend")
```

Then use:
```
"Switch to frontend"
"In backend, run pytest"
```

## Manual Setup for Better Integration

### **1. Enable Accessibility Permissions**
For UI scripting to work, ensure these apps have accessibility access:
- Terminal (where you run the voice assistant)
- Warp
- Python (if running from command line)

Go to: **System Preferences > Security & Privacy > Privacy > Accessibility**

### **2. Warp Configuration**
Create aliases in your shell (`.bashrc`, `.zshrc`, etc.) for common commands:
```bash
alias ll='ls -la'
alias gs='git status'
alias gp='git push'
```

### **3. Workflow Optimization**
For best results:
1. Keep Warp windows focused on different projects
2. Use descriptive window titles when possible
3. Set up custom aliases for frequently used terminals

## Limitations and Workarounds

### **Current Limitations:**
- Cannot read individual tab titles
- Cannot get current working directory
- Limited window information
- UI scripting may be unreliable if Warp UI changes

### **Workarounds:**
1. **Use custom aliases** to identify your terminals
2. **Keep projects in separate windows** rather than tabs
3. **Use launch configurations** for new session commands
4. **Combine with Warp's AI** for complex command generation

## Example Workflows

### **Frontend Development**
```
"Hey Jarvis"
"Switch to frontend"           # Warp window for React project
"Run development server"       # Executes 'npm run dev'
"Switch to backend"            # Different Warp window for API
"Run tests"                    # Executes test suite
```

### **Multiple Projects**
```
"Hey Jarvis"
"List terminals"               # Shows: Warp 1, Warp 2, Terminal 1, etc.
"Use Warp 1"
"Check git status"
"Switch to Warp 2" 
"Pull latest changes"
```

## Troubleshooting

### **Commands Not Executing**
1. Check accessibility permissions
2. Ensure Warp window is visible (not minimized)
3. Try manual command to verify voice recognition

### **Wrong Window Targeted**
1. Use explicit window numbers: "Warp 1", "Warp 2"
2. Set up custom aliases for better identification
3. Check with "List terminals" to see available options

### **UI Scripting Fails**
- The system will automatically fall back to launch configuration
- This opens a new tab with the command
- May be slower but more reliable

## Advanced Features

### **Creating Custom Launch Configurations**
You can manually create Warp launch configs for complex workflows:

```yaml
# ~/.warp/launch_configurations/my_project.yaml
---
name: my_project
windows:
  - tabs:
      - layout:
          cwd: "~/projects/frontend"
          commands:
            - exec: npm run dev
        color: blue
      - layout:
          cwd: "~/projects/backend"
          commands:
            - exec: python manage.py runserver
        color: green
```

Then use: `"Hey Jarvis, launch my project"`

### **Integration with Warp AI**
Since Warp has built-in AI, you can:
1. Use voice commands for basic operations
2. Switch to Warp AI for complex command generation
3. Combine both for optimal workflow

## Future Improvements

When Warp adds native AppleScript support, we'll be able to:
- Get detailed tab information
- Read current working directories
- Access command history
- Provide more accurate terminal targeting

Until then, this integration provides the best possible Warp support given the current limitations.