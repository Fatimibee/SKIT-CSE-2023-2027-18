"""
voice_input.py — mic -> Whisper transcription (fixed)
pip install openai-whisper sounddevice scipy numpy
"""
import sys
import numpy as np
import sounddevice as sd
import whisper
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
DURATION = 15
TEMP_FILE = "temp_audio.wav"

INPUT_DEVICE = None      # <- `python voice_input.py mic` se mila index yahan daalo
LANGUAGE = "en"          # "en" / "hi" / None (auto-detect, short clips pe unreliable)
MODEL_SIZE = "small"     # base quiet/noisy audio pe weak hai

print("Loading Whisper model...")
model = whisper.load_model(MODEL_SIZE)
print("Model loaded.\n")


def find_working_mic(test_duration: float = 2.0):
    """Har input device test karta hai; bolte raho. Highest RMS = working mic."""
    results = []
    for i, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] == 0:
            continue
        try:
            print(f"Testing [{i}] {dev['name']} ... speak!")
            a = sd.rec(int(test_duration * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                       channels=1, dtype="int16", device=i)
            sd.wait()
            rms = float(np.sqrt(np.mean(a.astype(np.float64) ** 2)))
            results.append((i, dev["name"], rms))
            print(f"   RMS = {rms:.1f}")
        except Exception as e:
            print(f"   skipped: {e}")
    results.sort(key=lambda r: r[2], reverse=True)
    print("\nTOP:")
    for i, n, r in results[:5]:
        print(f"  [{i}] {n} — RMS={r:.1f}")
    if results:
        print(f"\n👉 INPUT_DEVICE = {results[0][0]}")
    return results


def record_audio(duration: int = DURATION) -> np.ndarray:
    print(f"🎙️  Recording {duration}s... speak now (mic ke paas, clearly).")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype="float32", device=INPUT_DEVICE)
    sd.wait()
    audio = audio.flatten()

    peak = float(np.abs(audio).max())
    rms = float(np.sqrt(np.mean(audio ** 2)))
    print(f"✅ Done. peak={peak:.3f}, rms={rms:.4f}")

    if peak < 0.02:
        print("⚠️  Audio almost silent — INPUT_DEVICE galat hai ya Windows mic volume low hai.")

    # Normalize: quiet audio ko boost karo (Whisper ke liye zaroori)
    if peak > 0:
        audio = audio / peak * 0.9

    write(TEMP_FILE, SAMPLE_RATE, (audio * 32767).astype(np.int16))  # debug ke liye save
    return audio
def transcribe_audio(audio: np.ndarray, debug: bool = True) -> str:
    """Hindi / English / Hinglish audio (float32, 16kHz mono) -> English text."""
    print("📝 Transcribing...")

    # Sirf Hindi vs English me se choose (bn/mr jaisi galat detection ignore)
    mel = whisper.log_mel_spectrogram(whisper.pad_or_trim(audio)).to(model.device)
    _, probs = model.detect_language(mel)
    hi_score = probs.get("hi", 0) + probs.get("ur", 0)   # Urdu = Hindi-sounding
    en_score = probs.get("en", 0)
    lang = "hi" if hi_score >= en_score else "en"
    print(f"🌐 Using: {lang}  (hi={hi_score:.2f}, en={en_score:.2f})")

    common = dict(
        fp16=False,
        temperature=(0.0, 0.2, 0.4, 0.6),
        condition_on_previous_text=False,
        no_speech_threshold=0.6,
    )

    if lang == "en":
        return model.transcribe(audio, language="en", task="transcribe", **common)["text"].strip()

    # Hindi / Hinglish -> English
    if debug:
        original = model.transcribe(audio, language="hi", task="transcribe", **common)["text"].strip()
        print("🗣️  Original:", original)

    return model.transcribe(audio, language="hi", task="translate", **common)["text"].strip()

def record_and_transcribe() -> str:
    return transcribe_audio(record_audio())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mic":
        find_working_mic()
    else:
        text = record_and_transcribe()
        print("=" * 50)
        print("TRANSCRIPT:", text)
        print("=" * 50)