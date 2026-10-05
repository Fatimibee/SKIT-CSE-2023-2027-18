#  Voice Based Government Scheme Assistant using AI - AI Backend

> 🤖 AI-powered backend for processing **voice and text input**, extracting a structured user profile, checking eligibility, and speaking back recommended government schemes.

---

## 🔄 System Flow

```text
🎙️ Voice Input
      ↓
🗣️ Whisper (Speech-to-Text)
      ↓
📝 Transcript
      ↓
🌐 NVIDIA Riva (Translation)
      ↓
🧠 Profile Extraction (Gemini / Regex)
      ↓
👤 User Profile
      ↓
❓ Follow-up Questions (for missing fields)
      ↓
✅ Eligibility Engine (LangGraph + Gemini)
      ↓
🏆 Ranked Scheme Recommendations
      ↓
🔊 Voice Output (TTS)
```

---

## 📂 Project Files

| File | Purpose |
|---|---|
| 🎙️ `voice_input.py` | Takes voice input and converts speech to text using Whisper |
| 🌐 `translate.py` | Translates the transcript using NVIDIA Riva |
| 🔎 `extract.py` | Extracts user profile fields using Regex |
| 🤖 `extract_with_llm.py` | Extracts user profile using LangChain + Gemini |
| ❓ `follow_up.py` | Asks follow-up questions (voice) to fill in missing profile fields |
| 🔊 `tts.py` | Converts assistant responses to speech (gTTS, bilingual Hindi/English) |
| 📋 `schema.py` | Pydantic `UserProfile` schema and LangGraph workflow state schema |
| ⚙️ `config.py` | Loads API keys and configuration |
| 🔗 `nodes.py` | LangGraph node functions (parse profile, check eligibility, rank schemes) |
| 🕸️ `graph.py` | Builds and runs the LangGraph eligibility/recommendation workflow |
| 🗂️ `schemes_data.py` | Government scheme dataset (eligibility rules, benefits, documents) — temporary local data until Divyansh's Scheme API is ready |
| 🔁 `main_flow.py` | Connects the full pipeline: voice → translate → extract → follow-up → eligibility → recommendations |
| 📄 `generate_report.py` | Generates a project/status report |
| 📦 `requirements.txt` | Python dependencies |

---

## 👤 Profile Fields

The system extracts:

- 🎂 **Age**
- 💰 **Income**
- 💼 **Occupation**
- 📍 **State**
- ⚧️ **Gender**
- 🏷️ **Category**

---

## 🛠️ Setup

### 1️⃣ Create Virtual Environment

```powershell
python -m venv .venv
```

### 2️⃣ Activate Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the `AI_Backend` directory:

```env
GEMINI_API_KEY=your_gemini_api_key

FFMPEG_PATH = your_FFMPEG_PATH

NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_RIVA_SERVER=your_riva_server
NVIDIA_RIVA_FUNCTION_ID=your_function_id

# Scheme Data API (once Divyansh's backend is ready)
SCHEME_API_URL=your_scheme_api_url
```

> ⚠️ **Never commit `.env` or API keys to GitHub.**

---

## ▶️ Run the Modules

### 🎙️ Voice Input

```powershell
python voice_input.py
```

Captures audio and converts speech into a transcript using **Whisper**. Run `find_working_mic()` inside this file first if your mic isn't picking up sound correctly.

### 🌐 Translation

```powershell
python translate.py
```

Translates the transcript using **NVIDIA Riva**.

### 🔎 Regex Extraction

```powershell
python extract.py
```

Extracts profile information using **Regex-based rules**.

### 🤖 LLM Extraction

```powershell
python extract_with_llm.py
```

Extracts profile information using **LangChain + Google Gemini** with structured output.

### 🔊 Text-to-Speech

```powershell
python tts.py
```

Speaks sample English and Hindi text out loud using **gTTS**.

### ✅ Eligibility & Recommendation Engine

```powershell
python graph.py
```

Runs the LangGraph workflow standalone on a sample profile — checks eligibility (single batched Gemini call) and returns ranked scheme recommendations.

### 🔁 Full Pipeline

```powershell
python main_flow.py
```

Runs the complete end-to-end flow: records voice, transcribes, translates, extracts a profile, asks follow-up questions for any missing fields, and returns ranked scheme recommendations.

---

## 🧩 Tech Stack

| Technology | Usage |
|---|---|
| 🐍 **Python** | Backend development |
| 🎙️ **OpenAI Whisper** | Speech-to-Text |
| 🌐 **NVIDIA Riva** | Translation |
| 🦜 **LangChain** | LLM integration |
| ✨ **Google Gemini** | Profile extraction & eligibility reasoning |
| 🕸️ **LangGraph** | Eligibility & recommendation workflow orchestration |
| 🔊 **gTTS** | Text-to-speech (bilingual Hindi/English) |
| ✅ **Pydantic** | Data validation |
| 🔐 **python-dotenv** | Environment configuration |

---

## 📁 Project Structure

```text
AI_Backend/
│
├── 📁 .venv/
├── 🔐 .env
├── ⚙️ config.py
├── 🎙️ voice_input.py
├── 🌐 translate.py
├── 🔎 extract.py
├── 🤖 extract_with_llm.py
├── ❓ follow_up.py
├── 🔊 tts.py
├── 📋 schema.py
├── 🔗 nodes.py
├── 🕸️ graph.py
├── 🗂️ schemes_data.py
├── 🔁 main_flow.py
├── 📄 generate_report.py
├── 📦 requirements.txt
└── 📖 README.md
```

---

## 🧠 Extraction Approaches

### 🔎 Regex-Based Extraction

`extract.py`

✅ Fast  
✅ Lightweight  
✅ No LLM API call  
✅ Deterministic for known patterns

### 🤖 LLM-Based Extraction

`extract_with_llm.py`

✅ Handles natural language  
✅ Supports English / Hindi / Hinglish  
✅ More flexible sentence understanding  
✅ Uses structured Pydantic output

---

## ✅ Eligibility & Recommendation Engine

`schema.py` + `nodes.py` + `graph.py`

Built with **LangGraph**, the engine runs as a 3-step pipeline:

1. **Parse Profile** — normalizes extracted fields (age, income defaults)
2. **Check Eligibility** — sends the full profile + all schemes to Gemini in a **single batched call** (not one call per scheme), with a rule-based fallback if parsing fails
3. **Rank Schemes** — sorts eligible schemes by relevance/priority

Scheme data currently comes from a local dataset (`schemes_data.py`) and will switch to Divyansh's live Scheme API once ready — only `SCHEME_API_URL` in `.env` needs to change.

---

## ❓ Follow-up Question Handling

`follow_up.py`

If required profile fields (age, income, etc.) are missing after extraction:

1. Gemini generates a natural follow-up question
2. The question is **spoken aloud** via `tts.py`
3. The user's voice answer is recorded, transcribed, translated, and re-extracted
4. The answer is merged into the profile (up to 3 attempts per field)

---

## 🔊 Voice Output (TTS)

`tts.py`

Uses **gTTS** for bilingual speech output (Hindi + English) — chosen over offline options since it reliably supports Hindi, unlike most offline TTS engines.

---

## 🚀 Future Improvements

- 🏛️ Connect with the real government scheme database / API (Divyansh's backend)
- ⚡ Add **FastAPI APIs** to expose the full pipeline
- 🎯 Improve scheme ranking with relevance scoring, not just a fixed priority score
- 🗄️ Add database persistence for user profiles & recommendation history
- 🌐 Make follow-up questions respond in the user's spoken language (currently English only)

---

## 🔒 Security

Make sure `.gitignore` contains:

```gitignore
.env
.venv/
__pycache__/
*.pyc
temp_audio.wav
temp_recording.wav
```

Never push:

❌ API keys  
❌ `.env`  
❌ Virtual environment files  
❌ Recorded audio files

---

## Voice Based Government Scheme Assistant using AI

**Voice Based Government Scheme Assistant using AI** aims to make government schemes easier to discover by understanding a user's profile and helping identify schemes they may be eligible for.

> 🇮🇳 *Making government schemes more accessible through AI.*