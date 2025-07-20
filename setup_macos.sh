#!/bin/bash
# macOS setup script for voice terminal assistant

echo "Setting up Voice Terminal Assistant for macOS..."

# Install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install system dependencies
echo "Installing system dependencies..."
brew install portaudio ffmpeg

# Create virtual environment to avoid conflicts
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies in clean environment
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install openai-whisper sounddevice soundfile pyttsx3

# Install shell-genie (optional, can replace with local LLM)
echo "Installing shell-genie..."
pip install shell-genie

echo ""
echo "Setup complete!"
echo "To run: source venv/bin/activate && python voice_exec_macos.py"