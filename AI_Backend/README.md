#  Voice Based Government Scheme Assistant using AI - AI Backend

> 🤖 AI-powered backend for processing **voice and text input**, extracting a structured user profile, and matching it against government scheme eligibility.

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
🧠 Profile Extraction
      ↓
👤 User Profile
      ↓
✅ Eligibility Engine (LangGraph)
      ↓
🏆 Ranked Scheme Recommendations
```

---

## 📂 Project Files

| File | Purpose |
|---|---|
| 🎙️ `voice_input.py` | Takes voice input and converts speech to text using Whisper |
| 🌐 `translate.py` | Translates the transcript using NVIDIA Riva |
| 🔎 `extract.py` | Extracts user profile fields using Regex |
| 🤖 `extract_with_llm.py` | Extracts user profile using LangChain + Gemini |
| 📋 `schema.py` | Pydantic `UserProfile` schema (input validation) and LangGraph state schema for the eligibility workflow |
| ⚙️ `config.py` | Loads API keys and configuration |
| 🔗 `nodes.py` | LangGraph node functions (parse profile, check eligibility, rank schemes) |
| 🕸️ `graph.py` | Builds and runs the LangGraph eligibility/recommendation workflow |
| 🗂️ `schemes_data.py` | Sample government scheme dataset (eligibility rules, benefits, documents) |
| 🔁 `main_flow.py` | Connects the full pipeline: voice → translate → extract → eligibility → recommendations |
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
```

> ⚠️ **Never commit `.env` or API keys to GitHub.**

---

## ▶️ Run the Modules

### 🎙️ Voice Input

```powershell
python voice_input.py
```

Captures audio and converts speech into a transcript using **Whisper**.

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

### ✅ Eligibility & Recommendation Engine

```powershell
python graph.py
```

Runs the LangGraph workflow standalone on a sample profile — checks eligibility and returns ranked scheme recommendations.

### 🔁 Full Pipeline

```powershell
python main_flow.py
```

Runs the complete end-to-end flow: records voice, transcribes, translates, extracts a profile, and returns ranked scheme recommendations.

---

## 🧩 Tech Stack

| Technology | Usage |
|---|---|
| 🐍 **Python** | Backend development |
| 🎙️ **OpenAI Whisper** | Speech-to-Text |
| 🌐 **NVIDIA Riva** | Translation |
| 🦜 **LangChain** | LLM integration |
| ✨ **Google Gemini** | Profile extraction |
| 🕸️ **LangGraph** | Eligibility & recommendation workflow orchestration |
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
├── 📋 schema.py
├── 🔗 nodes.py
├── 🕸️ graph.py
├── 🗂️ schemes_data.py
├── 🔁 main_flow.py
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

`workflow_schema.py` + `nodes.py` + `graph.py`

Built with **LangGraph**, the engine runs as a 3-step pipeline:

1. **Parse Profile** — normalizes extracted fields (age, income defaults)
2. **Check Eligibility** — filters schemes from `schemes_data.py` based on profile rules
3. **Rank Schemes** — sorts eligible schemes by relevance/priority

Currently uses rule-based eligibility checks (age/income); next step is upgrading this to Gemini-based reasoning for more nuanced criteria (occupation, category, state).

---

## 🚀 Future Improvements

- 🧠 Upgrade eligibility checks to use Gemini-based reasoning (beyond age/income)
- ⚡ Add **FastAPI APIs** to expose the pipeline
- 💬 Add conversational follow-up for missing profile fields
- 🏛️ Connect with the real government scheme database (PostgreSQL)
- 🎯 Improve scheme matching and ranking logic
- 🗄️ Add database persistence for user profiles & recommendation history
- 🗣️ Add voice output (TTS) for responses

---

## 🔒 Security

Make sure `.gitignore` contains:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

Never push:

❌ API keys  
❌ `.env`  
❌ Virtual environment files

---

## Voice Based Government Scheme Assistant using AI

**Voice Based Government Scheme Assistant using AI** aims to make government schemes easier to discover by understanding a user's profile and helping identify schemes they may be eligible for.

> 🇮🇳 *Making government schemes more accessible through AI.*