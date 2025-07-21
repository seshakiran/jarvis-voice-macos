# 🎤 Speech Recognition Alternatives

## Why OpenAI Whisper Might Not Work Well

OpenAI Whisper can be **slow, resource-heavy, and unreliable** for real-time voice interaction. Here are **faster, better alternatives** for your voice terminal system.

---

## 🚀 **Available Alternatives**

### **1. Google Speech Recognition (Recommended)**
**File:** `voice_terminal_google.py`

**Pros:**
- ✅ **Fast and accurate**
- ✅ **Cloud-based, always updated**  
- ✅ **Works immediately**
- ✅ **Supports many languages**

**Cons:**
- ❌ Requires internet connection
- ❌ Sends audio to Google (privacy concern)

**Setup:**
```bash
venv/bin/pip install SpeechRecognition pyaudio
python3 voice_terminal_google.py
```

### **2. Vosk (Offline, Very Fast)**
**File:** `voice_terminal_vosk.py`

**Pros:**
- ✅ **Completely offline**
- ✅ **Very fast recognition**
- ✅ **Privacy-friendly**
- ✅ **Low resource usage**

**Cons:**
- ❌ Requires downloading model (~50MB)
- ❌ Slightly less accurate than cloud options

**Setup:**
```bash
# Download a model
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip

# Run the assistant
python3 voice_terminal_vosk.py
```

### **3. Ollama Integration (AI-Powered)**
**File:** `voice_terminal_ollama.py`

**Pros:**
- ✅ **Uses local LLM for command understanding**
- ✅ **Smart command interpretation**
- ✅ **Can understand complex requests**
- ✅ **Privacy-friendly**

**Cons:**
- ❌ Requires Ollama setup
- ❌ Uses more resources

**Setup:**
```bash
# Install Ollama
brew install ollama

# Pull a model
ollama pull llama3.2

# Run the assistant
python3 voice_terminal_ollama.py
```

### **4. macOS Built-in (Text Mode)**
**File:** `voice_terminal_macos_builtin.py`

**Pros:**
- ✅ **No external dependencies**
- ✅ **Perfect for testing**
- ✅ **Always works**
- ✅ **Great for debugging**

**Cons:**
- ❌ Text input only (no voice)
- ❌ Manual typing required

**Setup:**
```bash
# Works immediately
python3 voice_terminal_macos_builtin.py
```

---

## 🎯 **Which One Should You Use?**

### **For Best Performance:**
```bash
python3 voice_terminal_google.py
```
- Fast, accurate, works immediately
- Best choice if you have good internet

### **For Privacy/Offline:**
```bash
python3 voice_terminal_vosk.py  
```
- Download model first, then completely offline
- Great balance of speed and privacy

### **For AI-Powered Commands:**
```bash
python3 voice_terminal_ollama.py
```
- Best command understanding
- Can handle complex, natural requests

### **For Testing/Development:**
```bash
python3 voice_terminal_macos_builtin.py
```
- Type commands instead of speaking
- Perfect for testing the terminal routing logic

---

## 🛠️ **Setup Instructions**

### **Quick Start (Google):**
```bash
# Install dependencies
venv/bin/pip install SpeechRecognition pyaudio

# Test it works
python3 voice_terminal_google.py

# Say: "Hey Jarvis"
# Then: "list terminals"
# Then: "send hello to warp tab"
```

### **Offline Setup (Vosk):**
```bash
# Download model
curl -O https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip

# Install Vosk
venv/bin/pip install vosk pyaudio

# Run
python3 voice_terminal_vosk.py
```

### **Ollama Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Or via Homebrew
brew install ollama

# Start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull llama3.2

# Run voice terminal
python3 voice_terminal_ollama.py
```

---

## 🔧 **Performance Comparison**

| Method | Speed | Accuracy | Privacy | Setup | Internet |
|--------|-------|----------|---------|-------|----------|
| **Google** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Required |
| **Vosk** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | No |
| **Ollama** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | No |
| **Whisper** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | No |
| **Text Mode** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | No |

---

## 🎤 **Voice Commands That Work**

All versions support the same voice commands:

### **Terminal Management:**
```
"Hey Jarvis"
"list terminals"
"switch to warp"
"switch to frontend tab"
"switch to my project tab"
```

### **Send Text:**
```
"send hello to warp tab"
"send npm start to frontend tab"
"type git status to backend tab"
```

### **Contextual Commands:**
```
"in warp, list files"
"in frontend tab, run npm start"
"in my project tab, check git status"
```

### **Direct Commands:**
```
"list files"           # -> ls -la
"current directory"     # -> pwd
"clear screen"         # -> clear
"check git status"     # -> git status
"disk space"           # -> df -h
```

---

## 🐛 **Troubleshooting**

### **"No module named 'speech_recognition'"**
```bash
venv/bin/pip install SpeechRecognition
```

### **"No audio input device found"**
```bash
# Check microphone permissions
# System Preferences > Security & Privacy > Privacy > Microphone
# Add Terminal and Python
```

### **"Ollama connection failed"**
```bash
# Start Ollama service
ollama serve

# In another terminal, test it
ollama list
```

### **Vosk model not found**
```bash
# Download the model
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
```

### **Commands not executing in Warp**
- Make sure Warp window is visible
- Check accessibility permissions
- Try the text mode version first to test logic

---

## 🎯 **Recommended Setup**

1. **Start with text mode to test:**
   ```bash
   python3 voice_terminal_macos_builtin.py
   ```

2. **Once working, try Google for voice:**
   ```bash
   venv/bin/pip install SpeechRecognition pyaudio
   python3 voice_terminal_google.py
   ```

3. **For production use, set up Vosk (offline):**
   ```bash
   curl -O https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
   unzip vosk-model-en-us-0.22.zip
   python3 voice_terminal_vosk.py
   ```

**All alternatives are much faster and more reliable than OpenAI Whisper for this use case!** 🚀