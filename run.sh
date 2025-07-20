#!/bin/bash
# Voice Terminal Assistant runner with config check

cd "$(dirname "$0")"
source venv/bin/activate

# Check if configuration exists
if [ ! -f "$HOME/.voice_terminal_config.json" ]; then
    echo "🔧 No configuration found. Running initial setup..."
    python3 setup_config.py
    
    # Check if setup was successful
    if [ $? -ne 0 ] || [ ! -f "$HOME/.voice_terminal_config.json" ]; then
        echo "❌ Setup failed or was cancelled"
        exit 1
    fi
    
    echo ""
    echo "🎉 Setup complete! Starting Voice Terminal Assistant..."
    echo ""
fi

# Run the main application
python3 voice_exec_macos.py