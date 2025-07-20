import subprocess
import sounddevice as sd
import soundfile as sf
import whisper
import pyttsx3

engine = pyttsx3.init()

def speak(text):
    """Speaks the given text."""
    engine.say(text)
    engine.runAndWait()

def record_audio(filename, duration=5, samplerate=44100):
    """Records audio from the microphone."""
    print("Recording...")
    speak("Recording...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(filename, recording, samplerate)
    print("Recording finished.")
    speak("Recording finished.")

def transcribe_audio(filename):
    """Transcribes audio using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result["text"]

def get_shell_command(natural_language_query):
    """Gets a shell command from shell-genie."""
    try:
        process = subprocess.run(
            ["shell-genie", "ask", natural_language_query],
            capture_output=True,
            text=True,
            check=True,
        )
        return process.stdout.strip()
    except FileNotFoundError:
        return "shell-genie command not found. Please make sure it is installed and in your PATH."
    except subprocess.CalledProcessError as e:
        return f"shell-genie returned an error: {e.stderr}"


def main():
    """Main function to run the voice to terminal assistant."""
    audio_filename = "temp_audio.wav"
    while True:
        try:
            input("Press Enter to start recording...")
            record_audio(audio_filename)
            natural_language_query = transcribe_audio(audio_filename)
            print(f"You said: {natural_language_query}")
            speak(f"You said: {natural_language_query}")

            if natural_language_query.lower().strip() in ["exit", "quit"]:
                break

            shell_command = get_shell_command(natural_language_query)

            if shell_command:
                print(f"Suggested command: {shell_command}")
                speak(f"Suggested command: {shell_command}")
                confirmation = input("Execute? [y/n]: ")
                if confirmation.lower() == "y":
                    speak("Executing command.")
                    process = subprocess.run(
                        shell_command, shell=True, capture_output=True, text=True
                    )
                    print(process.stdout)
                    print(process.stderr)
                    if process.stdout:
                        speak(process.stdout)
                    if process.stderr:
                        speak(process.stderr)
        except Exception as e:
            print(f"An error occurred: {e}")
            speak(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
