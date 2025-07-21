# 🎤 Universal Tab Name Support

## ✨ **Now Works with ANY Tab Name!**

Your voice terminal system now supports **any tab name** you use in Warp, not just hardcoded names. This means you can use your actual project names and workflows.

---

## 🎯 **Supported Voice Command Patterns**

### **1. Send Text to Any Tab**
```
"Send [text] to [ANY_NAME] tab"
```

**Examples:**
- `"Send hello to frontend tab"`
- `"Send npm start to react tab"`
- `"Send git status to my awesome project tab"`
- `"Type python app.py to django tab"`
- `"Send kubectl get pods to kubernetes tab"`

### **2. Contextual Commands to Any Tab**
```
"In [ANY_NAME] tab, [command]"
```

**Examples:**
- `"In frontend tab, run npm start"`
- `"In backend tab, run python manage.py runserver"`
- `"In docker tab, docker-compose up"`
- `"In api tab, check git status"`
- `"In my project tab, list files"`

### **3. Switch to Any Tab**
```
"Switch to [ANY_NAME] tab"
"Use [ANY_NAME] tab"
```

**Examples:**
- `"Switch to frontend tab"`
- `"Use backend tab"`
- `"Switch to my awesome project tab"`
- `"Use development tab"`

---

## 🚀 **Real-World Examples**

### **Web Development Workflow:**
```
"Hey Jarvis"
"Switch to frontend tab"
"In frontend tab, run npm start"
"Send npm run build to frontend tab"
"Switch to backend tab" 
"In backend tab, run python app.py"
```

### **DevOps Workflow:**
```
"Hey Jarvis"
"In docker tab, docker-compose up"
"Switch to kubernetes tab"
"Send kubectl get pods to kubernetes tab"
"In monitoring tab, check logs"
```

### **Multi-Project Development:**
```
"Hey Jarvis"
"Switch to client project tab"
"In client project tab, run tests"
"Switch to server project tab"
"Send git status to server project tab"
```

---

## 🔍 **How It Works**

### **Pattern Recognition:**
- **Any phrase ending with "tab"** targets Warp terminal
- **"warp" by itself** also targets Warp terminal
- **Other terminal names** (terminal, iterm, vscode) target their respective apps

### **Tab Name Examples That Work:**
- ✅ `frontend tab`
- ✅ `backend tab`
- ✅ `api tab`
- ✅ `database tab`
- ✅ `my awesome project tab`
- ✅ `work tab`
- ✅ `development tab`
- ✅ `react app tab`
- ✅ `django server tab`
- ✅ `docker compose tab`

### **Important Notes:**
1. **Warp Limitation:** Due to Warp's lack of AppleScript support, the system can't read actual tab titles
2. **Window-Level Targeting:** Commands target Warp windows, not individual tabs
3. **Multiple Warp Windows:** If you have multiple Warp windows, use `warp 1`, `warp 2`, etc.

---

## 🎛️ **Advanced Usage**

### **Multiple Warp Windows:**
```
"Switch to warp 1"          # First Warp window
"Switch to warp 2"          # Second Warp window  
"In warp 1, list files"     # Contextual to specific window
```

### **Custom Aliases:**
You can set up custom aliases for frequently used tabs:

```python
# In your voice terminal session
discovery.set_terminal_alias("Warp:1", "frontend")
discovery.set_terminal_alias("Warp:2", "backend")
```

Then use:
```
"Switch to frontend"
"In backend, run tests"
```

### **Mixing Tab Names and Aliases:**
```
"Send hello to frontend tab"     # Uses pattern matching
"Switch to frontend"             # Uses custom alias  
"In my project tab, run build"   # Uses pattern matching
```

---

## 🧪 **Testing Your Setup**

### **Quick Test Commands:**
```bash
# Test command parsing (no audio)
python3 test_any_tab_name.py

# Test realistic scenarios  
python3 quick_voice_test.py

# Full voice terminal
python3 voice_terminal_main.py
```

### **Verify Tab Support:**
1. **Start voice terminal:** `python3 voice_terminal_main.py`
2. **Say wake word:** `"Hey Jarvis"`
3. **Test your tab:** `"Send hello to [YOUR_TAB_NAME] tab"`
4. **Check contextual:** `"In [YOUR_TAB_NAME] tab, list files"`

---

## 🛠️ **Troubleshooting**

### **Tab Not Recognized:**
- ✅ **Make sure to say "tab"**: `"frontend tab"` not just `"frontend"`
- ✅ **Check Warp is running**: System needs at least one Warp window open
- ✅ **Use clear pronunciation**: Speak tab names clearly
- ✅ **Try variations**: `"my project tab"` vs `"project tab"`

### **Commands Not Executing:**
- ✅ **Check Accessibility**: System Preferences > Security & Privacy > Privacy > Accessibility
- ✅ **Warp Focus**: Commands work better when Warp window is visible
- ✅ **Try Direct Warp**: Use `"send hello to warp"` to test basic functionality

### **Multiple Tabs in One Window:**
- ⚠️ **Limitation**: Can't target individual tabs within same Warp window
- ✅ **Workaround**: Use separate Warp windows for different projects
- ✅ **Alternative**: Use launch configurations (creates new tabs automatically)

---

## 📈 **Performance Notes**

### **Command Execution Methods:**
1. **UI Scripting** (Primary): Direct keystroke simulation to active Warp window
2. **Launch Config** (Fallback): Creates new tab with pre-configured command

### **When Each Method Is Used:**
- **UI Scripting**: When Warp window is accessible and focused
- **Launch Config**: When UI scripting fails or window not accessible

### **Optimization Tips:**
- Keep Warp windows visible for better UI scripting success
- Use descriptive tab names for better voice recognition
- Set up custom aliases for frequently used terminals

---

## 🎉 **Summary**

Your voice terminal now supports **unlimited tab names**! Use any naming convention that works for your projects:

- ✅ **Project names**: `"my awesome app tab"`
- ✅ **Technology stacks**: `"react frontend tab"`, `"django backend tab"`
- ✅ **Environment names**: `"development tab"`, `"staging tab"`, `"production tab"`
- ✅ **Workflow stages**: `"build tab"`, `"test tab"`, `"deploy tab"`

**The system adapts to YOUR workflow, not the other way around!** 🚀