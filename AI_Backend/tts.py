"""
tts.py
-------
Text-to-Speech module — converts the assistant's follow-up questions
(and any other response text) into spoken audio.

Uses gTTS (Google Text-to-Speech) — free, no API key, and properly
supports Hindi + English, unlike offline options (pyttsx3) which often
can't speak Hindi correctly, and NVIDIA Riva TTS which only hosts
English as a simple API (Hindi requires self-hosting with a GPU).

Install:
    pip install gTTS playsound==1.2.2

Needs internet access (calls Google's TTS service).
"""

from gtts import gTTS
from playsound import playsound
import os
import tempfile

LANG_CODE_MAP = {
    "en": "en",
    "hi": "hi",
}


def speak(text: str, lang: str = "en"):
    """
    Converts text to speech and plays it immediately.

    Args:
        text: the text to speak
        lang: "en" for English, "hi" for Hindi
    """
    lang_code = LANG_CODE_MAP.get(lang, "en")
    print(f"🔊 Speaking ({lang_code}): {text}")

    tts = gTTS(text=text, lang=lang_code)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_path = tmp_file.name

    tts.save(tmp_path)
    playsound(tmp_path)
    os.remove(tmp_path)


if __name__ == "__main__":
    speak("Hello! Could you please tell me your age and income?", lang="en")
    speak("नमस्ते! क्या आप मुझे अपनी उम्र और आय बता सकते हैं?", lang="hi")