# 🎤 Voice Terminal Assistant

A sophisticated voice-controlled terminal assistant for macOS that converts natural language into shell commands. Built with local speech processing for privacy and speed.

## ✨ Features

- **🎯 Natural Language Processing**: Speak commands naturally - "list all files" → `ls -la`
- **🔄 Session-Based Conversations**: Stay active after wake word, no need to repeat "Hey Jarvis"
- **⚡ Smart Auto-Execution**: Commands execute automatically after 2 seconds (configurable)
- **🎙️ Local Processing**: Uses OpenAI Whisper locally - no cloud dependencies
- **🛡️ Safe Execution**: Always confirms before running commands
- **📝 Extensive Command Library**: Supports 100+ command variations across categories:
  - File operations (ls, cd, mkdir, rm, cp, mv, etc.)
  - System info (ps, top, df, free, uname, etc.)
  - Git operations (status, add, commit, push, pull, etc.)
  - Network tools (ping, curl, wget, etc.)
  - Package management (brew, npm, pip, apt)
  - And much more!

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/voice-terminal-assistant.git
cd voice-terminal-assistant

# Run setup (installs dependencies and creates virtual environment)
chmod +x setup_macos.sh
./setup_macos.sh
```

### First Run

```bash
# Start the assistant
./run.sh
```

On first run, you'll be prompted to:
1. Set your assistant's name (e.g., "Jarvis", "Friday", "Assistant")
2. Configure auto-execution timeout (recommended: 2 seconds)

### Usage

1. **Wake Word**: Say "Hey [YourAssistantName]" to activate
2. **Give Command**: Speak naturally - "What directory am I in?"
3. **Auto-Execute**: Commands execute automatically after timeout
4. **Session Mode**: Continue giving commands without repeating wake word
5. **Sleep**: Say "sleep" or "go to sleep" to return to wake word mode

## 🎯 Example Conversations

```
You: "Hey Jarvis"
Jarvis: "Hello! I'm listening. What can I do for you?"

You: "What directory am I in?"
Jarvis: "Suggested command: pwd" → executes → shows current directory

You: "List all the files here"
Jarvis: "Suggested command: ls -la" → executes → shows file listing

You: "Create a new folder called projects"
Jarvis: "Suggested command: mkdir projects" → executes

You: "Sleep"
Jarvis: "Going to sleep"
```

## 📁 Project Structure

```
voice-terminal-assistant/
├── voice_exec_macos.py      # Main application
├── setup_config.py          # Initial configuration setup
├── config_manager.py        # Settings management
├── command_mappings.json    # Comprehensive command database
├── setup_macos.sh          # Dependency installation
├── run.sh                  # Application launcher
└── README.md              # Documentation
```

## ⚙️ Configuration

### Change Settings

```bash
# Modify assistant name or timeout
python3 config_manager.py
```

### Command Mappings

Edit `command_mappings.json` to add new command patterns:

```json
{
  "file_operations": {
    "ls -la": [
      "list files", "show files", "what files are here"
    ],
    "mkdir {name}": [
      "create folder", "make directory", "new folder"
    ]
  }
}
```

### Session Timeouts

Modify in `voice_exec_macos.py`:
- `command_wait_timeout`: How long to wait for commands (default: 5s)
- `session_timeout`: Total session duration (default: 30s)
- `confirmation_timeout`: Auto-execution delay (default: 2s)

## 🔧 Advanced Features

### Parameterized Commands

The assistant intelligently handles commands with parameters:

- "Create folder my_project" → `mkdir my_project`
- "Delete file test.txt" → `rm test.txt`
- "Copy file1 to file2" → `cp file1 file2`

### Session Commands

- **"sleep"** / **"go to sleep"**: Return to wake word mode
- **"continue"** / **"stay active"**: Extend session
- **"exit"** / **"quit"**: Close application

### Smart Responses

- **Conversational**: "I'm just thinking" → "Got it" (no execution)
- **Unknown Commands**: Provides helpful suggestions
- **Long Commands**: Announces "Running command, this might take a moment"

## 🛠️ Technical Details

### Dependencies

- **OpenAI Whisper**: Local speech-to-text
- **sounddevice**: Audio recording
- **pyttsx3**: Text-to-speech
- **shell-genie**: Natural language to shell (fallback)

### Audio Processing

- **Voice Activation**: Automatically detects speech
- **Noise Filtering**: Ignores background noise
- **Feedback Prevention**: Smart delays prevent TTS loops

### Privacy & Security

- **Local Processing**: All speech processing happens on your machine
- **No Cloud**: No data sent to external services
- **Command Confirmation**: Always shows commands before execution
- **Safe Defaults**: Non-destructive commands preferred

## 🐛 Troubleshooting

### Audio Issues

```bash
# Check microphone permissions in System Preferences > Security & Privacy > Microphone
# Ensure Terminal has microphone access

# Test audio devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

### Dependencies

```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade openai-whisper sounddevice soundfile pyttsx3 shell-genie
```

### Reset Configuration

```bash
# Remove config file to reset
rm ~/.voice_terminal_config.json
./run.sh  # Will prompt for new setup
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Add new command patterns to `command_mappings.json`
4. Test your changes: `./run.sh`
5. Submit a pull request

### Adding New Commands

To add support for new commands, edit `command_mappings.json`:

```json
{
  "your_category": {
    "your-command": [
      "natural language phrase 1",
      "natural language phrase 2"
    ]
  }
}
```

## 📜 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for excellent local speech recognition
- Shell-genie for natural language to shell inspiration
- The open-source community for amazing Python audio libraries

---

**Note**: This project requires macOS and has been tested on macOS 11.0+. For other platforms, audio device handling may need modification.