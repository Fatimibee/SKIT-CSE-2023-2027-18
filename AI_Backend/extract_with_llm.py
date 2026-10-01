"""
NLP Processing step (Profile-Based Flow, 5A).
Raw transcript (Whisper / typed) -> structured profile for the Eligibility Engine.
"""

import json

from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_API_KEY
from schema import UserProfile


REQUIRED_FIELDS = ["age", "income", "occupation", "state", "gender", "category"]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)
structured_llm = llm.with_structured_output(UserProfile)


EXTRACTION_PROMPT = """
You are an information extraction system for a government scheme assistant.

Extract the user's profile information from the message below.
The message may be in English, Hindi, or Hinglish.

Fields:
- age: integer, or null
- income: ANNUAL household income in INR as an integer, or null
- occupation: string, or null
- state: Indian state name, or null
- gender: male/female/other, or null
- category: General/OBC/SC/ST/EWS, or null

Rules:
- Extract only information explicitly present or clearly implied. Never guess.
- If a field is not mentioned, return null.
- Convert spoken numbers to integers: "one lakh fifty thousand" = 150000, "1.5 lakh" = 150000.
- Income 0 is a VALID value, NOT null: "zero", "nothing", "no income", "not earning" = 0.
- If income is given without saying monthly or yearly, treat it as annual.
  If clearly monthly ("per month"), multiply by 12.
- Normalize Indian state names. Do not add fields outside the schema.
{context}
User message:

\"\"\"
{transcript}
\"\"\"
"""


def extract_profile(transcript: str, expected_field: str | None = None) -> dict:
    """
    Returns {"profile": {...}, "missing_fields": [...]}.

    expected_field: follow-up me jis field ka jawab aa raha hai
    (e.g. "income"), taaki bare answers ("10,000", "zero", "18") samajh aayein.
    """
    context = ""
    if expected_field:
        context = (
            f"\nContext: the assistant just asked the user for their '{expected_field}'. "
            f"The message is probably a short direct answer to that question, so a bare "
            f"value (e.g. '10,000', 'zero', '18', 'OBC') should be assigned to '{expected_field}'.\n"
        )

    prompt = EXTRACTION_PROMPT.format(transcript=transcript, context=context)

    try:
        result = structured_llm.invoke(prompt)
        profile = result.model_dump() if result else {f: None for f in REQUIRED_FIELDS}
    except Exception as error:
        print(f"LLM extraction error: {error}")
        profile = {f: None for f in REQUIRED_FIELDS}

    missing_fields = [f for f in REQUIRED_FIELDS if profile.get(f) is None]
    return {"profile": profile, "missing_fields": missing_fields}


if __name__ == "__main__":
    tests = [
        ("I am a 45 year old farmer from Rajasthan, my income is around one lakh fifty "
         "thousand rupees, I am male, general category.", None),
        ("My income is 10,000 rupees", "income"),
        ("zero", "income"),
        ("18", "age"),
    ]
    for text, field in tests:
        print(text, "->", json.dumps(extract_profile(text, field)["profile"], ensure_ascii=False))