"""
main_flow.py
-------------
Single connector file — links everything built so far into one flow:

    Mic Recording
        --Whisper (voice_input.py)-->        Native language transcript
        --Riva Translate (translate.py)-->   English text
        --Gemini Extract (extract.py)-->     Structured profile (age, income, etc.)
        --LangGraph Workflow (workflow.py)--> Ranked scheme recommendations

This is the current end-to-end state of the AI & Recommendation Engine.
Run this file directly to test the full pipeline in one go.

Requires (same folder):
    voice_input.py, translate.py, extract.py, config.py, workflow.py,
    schemes_data.py, .env (with GEMINI_API_KEY, NVIDIA_API_KEY)
"""

from voice_input import record_and_transcribe
from translate import translate_text
from extract import extract_profile
from graph import run_recommendation_workflow


def run_full_flow(source_lang: str = "hi") -> dict:
    """
    Runs the complete pipeline: voice -> transcript -> translation ->
    structured profile -> eligibility check -> ranked recommendations.
    """

    # 1. Voice -> transcript (Whisper)
    print("STEP 1: Recording & transcribing voice input...")
    transcript = record_and_transcribe()
    print("Transcript:", transcript)

    # 2. Transcript -> English (Riva Translate)
    if source_lang != "en":
        print("\nSTEP 2: Translating to English...")
        translated_text = translate_text(transcript, source_language=source_lang, target_language="en")
        print("Translated:", translated_text)
    else:
        translated_text = transcript
        print("\nSTEP 2: Skipped (already English)")

    # 3. English text -> structured profile (Gemini)
    print("\nSTEP 3: Extracting structured profile...")
    extraction_result = extract_profile(translated_text)
    profile = extraction_result["profile"]
    missing_fields = extraction_result["missing_fields"]
    print("Profile:", profile)
    print("Missing fields:", missing_fields)

    if missing_fields:
        print(f"\n⚠️  Cannot run eligibility check — missing: {', '.join(missing_fields)}")
        return {
            "transcript": transcript,
            "translated_text": translated_text,
            "profile": profile,
            "missing_fields": missing_fields,
            "recommendations": None,
        }

    # 4. Structured profile -> eligibility + ranked schemes (LangGraph)
    print("\nSTEP 4: Running eligibility & recommendation engine...")
    recommendation_result = run_recommendation_workflow(profile)
    print("Eligible schemes found:", recommendation_result["eligible_count"])

    return {
        "transcript": transcript,
        "translated_text": translated_text,
        "profile": profile,
        "missing_fields": missing_fields,
        "recommendations": recommendation_result["recommendations"],
    }


if __name__ == "__main__":
    result = run_full_flow(source_lang="hi")

    print("\n" + "=" * 50)
    print("FINAL OUTPUT")
    print("=" * 50)

    if result["recommendations"]:
        for i, scheme in enumerate(result["recommendations"], start=1):
            print(f"\n{i}. {scheme['name']}")
            print(f"   Benefits: {scheme['benefits']}")
            print(f"   Required Documents: {', '.join(scheme['required_documents'])}")
    else:
        print("No recommendations yet — check missing_fields above.")