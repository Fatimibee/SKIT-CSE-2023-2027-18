"""
follow_up.py — missing profile fields ek-ek karke poochta hai (voice).

Flow per field:
    Gemini se ek chhota sawaal -> voice answer (English text) -> extract -> merge
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from config import GEMINI_API_KEY
from voice_input import record_and_transcribe   # seedha English text deta hai
from extract_with_llm import extract_profile             # agar file ka naam extract2.py hai: from extract2 import extract_profile

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3,
)

MAX_ATTEMPTS_PER_FIELD = 2

FIELD_QUESTION_HINTS = {
    "age": "their age",
    "income": "their annual household income in rupees",
    "occupation": "their occupation or job",
    "state": "which Indian state they live in",
    "gender": "their gender",
    "category": "their category (General/OBC/SC/ST/EWS)",
}


def _is_empty(v) -> bool:
    """None / '' = empty. 0 valid value hai (income = 0)."""
    return v is None or (isinstance(v, str) and not v.strip())


def generate_follow_up_question(missing_fields: list) -> str:
    hints = [FIELD_QUESTION_HINTS.get(f, f) for f in missing_fields]
    prompt = (
        "You are a friendly voice assistant helping an Indian citizen find "
        "government schemes. Politely ask ONE short question (1 sentence) "
        f"to find out: {', '.join(hints)}. "
        "Keep it simple and conversational. Respond with ONLY the question."
    )
    return llm.invoke([HumanMessage(content=prompt)]).content.strip()


def _merge_profile(original: dict, new_data: dict) -> dict:
    """Sirf empty fields bharta hai; existing data overwrite nahi hota."""
    merged = dict(original)
    for key, value in new_data.items():
        if not _is_empty(value) and _is_empty(merged.get(key)):
            merged[key] = value
    return merged


def resolve_missing_fields(profile: dict, missing_fields: list, source_lang: str = "en") -> dict:
    """
    Har missing field ek-ek karke poochta hai (max MAX_ATTEMPTS_PER_FIELD baar).
    source_lang sirf compatibility ke liye hai (voice_input already English deta hai).
    Updated profile return karta hai.
    """
    current = dict(profile)
    failed = []

    for field in missing_fields:
        tries = 0
        while _is_empty(current.get(field)) and tries < MAX_ATTEMPTS_PER_FIELD:
            tries += 1

            question = generate_follow_up_question([field])
            print(f"\n🤖 Assistant: {question}")

            answer = record_and_transcribe()
            print("You said:", answer)
            if not answer:
                continue

            result = extract_profile(answer, expected_field=field)
            print("🔎 Extracted:", result["profile"])
            current = _merge_profile(current, result["profile"])

        if _is_empty(current.get(field)):
            failed.append(field)

    if failed:
        print(f"\n⚠️  Collect nahi hua: {', '.join(failed)}")
        print("   Partial profile ke saath aage badh rahe hain — results incomplete ho sakte hain.")

    return current


if __name__ == "__main__":
    sample = {"age": 45, "income": None, "occupation": "farmer",
              "state": None, "gender": "male", "category": None}
    print("\nFinal profile:", resolve_missing_fields(sample, ["income", "state", "category"]))