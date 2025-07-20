#!/usr/bin/env python3
"""
Simple voice recognition test to debug microphone issues
"""

import sounddevice as sd
import soundfile as sf
import whisper
import tempfile
import os

def test_microphone():
    """Test microphone and voice recognition"""
    print("🎤 Testing microphone and voice recognition...")
    print("🔊 Say something in the next 3 seconds...")
    
    # Record audio
    samplerate = 44100
    duration = 3  # seconds
    
    try:
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
        sd.wait()
        
        # Check if audio was captured
        max_amplitude = float(recording.max())
        print(f"📊 Max audio amplitude: {max_amplitude}")
        
        if max_amplitude < 0.01:
            print("❌ Very low audio detected. Check microphone permissions.")
            print("💡 Go to System Preferences > Security & Privacy > Microphone")
            print("   Make sure Terminal.app or your terminal has microphone access.")
            return
        
        # Save and transcribe
        temp_file = os.path.join(tempfile.gettempdir(), "test_voice.wav")
        sf.write(temp_file, recording, samplerate)
        
        print("🔄 Transcribing...")
        model = whisper.load_model("base")
        result = model.transcribe(temp_file)
        
        print(f"📝 You said: '{result['text'].strip()}'")
        
        if "jarvis" in result['text'].lower():
            print("✅ Wake word detected successfully!")
        else:
            print("💡 Try saying 'hey jarvis' clearly")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_microphone()