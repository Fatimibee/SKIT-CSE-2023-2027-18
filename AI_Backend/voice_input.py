import whisper  
import sounddevice as sd  
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv



SAMPLE_RATE = 16000  # Whisper expects 16kHz audio
DURATION = 5  # Duration of recording in seconds
TEMP_FILE = "temp_audio.wav"  # Temporary file to save the recorded audio


load_dotenv()

FFMPEG_PATH = os.getenv("FFMPEG_PATH")
os.environ["PATH"] += os.pathsep + FFMPEG_PATH

# Load the Whisper model
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully.")



def record_audio(duration=DURATION, sample_rate=SAMPLE_RATE):

    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * sample_rate),
                    samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished

    write(TEMP_FILE, sample_rate, audio)  # Save the recorded audio to a temporary file
    print(f"Audio recorded and saved to {TEMP_FILE}.")

    return TEMP_FILE

def transcribe_audio(file_path):
    print("Transcribing audio...")

    result = model.transcribe(file_path , fp16 = False)

    return result['text'].strip() # Return the transcribed text without leading/trailing whitespace


def record_and_transcribe():
    audio_file = record_audio()
    transcription = transcribe_audio(audio_file)
    print("Transcription completed.")
    return transcription


if __name__ == "__main__":
    transcription = record_and_transcribe()
    print("="*50)
    print("Transcribed Text:", transcription)
    print("="*50)