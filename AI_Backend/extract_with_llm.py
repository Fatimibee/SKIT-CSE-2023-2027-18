"""
NLP Processing step (Profile-Based Flow, 5A).

Takes a raw transcript from Whisper or typed text and extracts
the structured profile required by the Eligibility Engine.
"""

import json

from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_API_KEY
from schema import UserProfile


REQUIRED_FIELDS = [
    "age",
    "income",
    "occupation",
    "state",
    "gender",
    "category",
]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)

structured_llm = llm.with_structured_output(UserProfile)


EXTRACTION_PROMPT = """
You are an information extraction system for a government scheme
assistant.

Extract the user's profile information from the message below.

The message may be written in English, Hindi, or Hinglish.

Extract:

- age: integer, or null
- income: annual income in INR as an integer, or null
- occupation: string, or null
- state: Indian state name, or null
- gender: male/female/other, or null
- category: General/OBC/SC/ST/EWS, or null

Rules:

- Extract only information explicitly present or clearly implied.
- Never guess missing information.
- If a field is missing or unclear, return null.
- Convert spoken numbers into integers.
- "one lakh fifty thousand" means 150000.
- "1.5 lakh" means 150000.
- Normalize Indian state names where possible.
- Do not add any fields outside the schema.

User message:

\"\"\"
{transcript}
\"\"\"
"""


def extract_profile(transcript: str) -> dict:
    """
    Extract structured profile from a raw transcript.

    Returns:
        {
            "profile": {...},
            "missing_fields": [...]
        }
    """

    prompt = EXTRACTION_PROMPT.format(
        transcript=transcript
    )

    try:
        result = structured_llm.invoke(prompt)

        profile = result.model_dump()

    except Exception as error:
        print(f"LLM extraction error: {error}")

        profile = {
            field: None
            for field in REQUIRED_FIELDS
        }

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if profile.get(field) is None
    ]

    return {
        "profile": profile,
        "missing_fields": missing_fields,
    }


if __name__ == "__main__":

    sample_transcript = (
        "I am a 45 year old farmer from Rajasthan, "
        "my income is around one lakh fifty thousand rupees, "
        "I am male, general category."
    )

    result = extract_profile(sample_transcript)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )