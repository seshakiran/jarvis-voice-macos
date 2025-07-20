# 🔧 Troubleshooting Guide

## Problem: Assistant loops without detecting wake word

### 1. **Test Voice Recognition**:
```bash
python3 test_voice.py
```
This will test if your microphone is working.

### 2. **Check Microphone Permissions**:
- Go to **System Preferences** > **Security & Privacy** > **Privacy** > **Microphone**
- Make sure **Terminal.app** (or your terminal) has microphone access ✅
- If not listed, run the voice assistant once to trigger permission request

### 3. **Audio Input Issues**:
- Speak clearly and close to microphone
- Try different wake phrases: "hey jarvis", "hi jarvis", "hello jarvis"
- Ensure no background noise is interfering

### 4. **Terminal Routing Issues**:
Check your config has terminal routing enabled:
```bash
cat ~/.voice_terminal_config.json
```
Should show: `"enabled": true` under `terminal_routing`

## Problem: "No terminals found"

### 1. **Open Terminal Applications**:
- Open **Terminal.app** (at least one window)
- Or open **iTerm2** 
- Or open **VS Code** with integrated terminal

### 2. **Test Terminal Discovery**:
```python
from terminal_management import TerminalDiscovery
discovery = TerminalDiscovery()
terminals = discovery.get_available_terminals(force_refresh=True)
for t in terminals:
    print(f"Found: {t.window.display_name}")
```

## Problem: Text not sending to terminals

### 1. **Check AppleScript Permissions**:
- System Preferences > Security & Privacy > Privacy > **Accessibility**
- Add and enable **Terminal.app** or your terminal app

### 2. **Test Text Sending**:
Try the wake word first, then:
- "show terminals" (should list available terminals)
- "send text hello to terminal 1" (should send "hello" + Enter)

## Common Solutions

### Voice Recognition Issues:
1. **Speak clearly** - Whisper AI needs clear audio
2. **Reduce background noise** - Use in quiet environment  
3. **Check microphone** - Test with other voice apps first
4. **Try shorter phrases** - "hey jarvis" works better than long sentences

### Terminal Access Issues:
1. **Grant permissions** - macOS needs explicit permission for mic + accessibility
2. **Run as admin** - Some AppleScript features need elevated access
3. **Open target terminals** - Make sure terminals are actually running

### Audio Buffer Issues:
- If you get continuous loops, try restarting the assistant
- Check audio device settings in System Preferences

## Quick Test Commands

Once wake word works, test these:
- **"show terminals"** - Lists available terminals
- **"send text hello"** - Sends "hello" to current target  
- **"say yes to terminal 1"** - Sends "yes" to terminal 1
- **"switch to terminal 2"** - Changes target terminal

## Still Having Issues?

1. Check the terminal output for specific error messages
2. Ensure all dependencies are installed: `./setup_macos.sh`
3. Try running in a quiet environment
4. Make sure your Mac has a working microphone