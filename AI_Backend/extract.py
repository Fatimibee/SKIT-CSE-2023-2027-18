import re
REQUIRED_FIELDS = [
    "age" , "income" , "occupation" , "state" , "gender" , "category"
]

INDIAN_STATES = [
    "rajasthan", "maharashtra", "uttar pradesh", "bihar", "madhya pradesh",
    "gujarat", "punjab", "haryana", "kerala", "tamil nadu", "karnataka",
    "west bengal", "odisha", "assam", "jharkhand", "chhattisgarh", "telangana",
    "andhra pradesh", "delhi", "goa",
]

OCCUPATION_KEYWORDS = [
    "farmer", "labourer", "laborer", "teacher", "student", "shopkeeper",
    "driver", "carpenter", "mechanic", "housewife", "self employed",
    "government employee", "private employee", "unemployed",
]


CATEGORY_KEYWORDS = {
    "general": "General",
    "obc": "OBC",
    "sc": "SC",
    "st": "ST",
    "ews": "EWS",
}

# converts common spoken number phrases to plain integers (basic coverage)
NUMBER_WORDS = {
    "lakh": 100000,
    "lac": 100000,
    "thousand": 1000,
    "crore": 10000000,
}

# Age Extraction 

def _extract_age(text):
    match = re.search(r"\b(\d{1,3})\s*(years?|yr)?\s*(old)?\b" , text.lower())

    if match :
        age = int(match.group(1))
        if 0 < age < 120 :
            return age
    return None


# Income Extraction

def _extract_income(text: str):
    text_lower = text.lower()
 
    # pattern like "1.5 lakh" or "one lakh fifty thousand"
    lakh_match = re.search(r"(\d+(\.\d+)?)\s*lakh", text_lower)
    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)
 
    thousand_match = re.search(r"(\d+(\.\d+)?)\s*thousand", text_lower)
    if thousand_match:
        return int(float(thousand_match.group(1)) * 1000)
 
    # plain number near "income" or "rupees"
    income_match = re.search(r"(income|earn|salary)[^\d]{0,15}(\d{4,8})", text_lower)
    if income_match:
        return int(income_match.group(2))
 
    return None

#Occupation Extraction

def _extract_occupation(text):
    text_lower = text.lower()
    for keyword in OCCUPATION_KEYWORDS :
        if keyword in text_lower:
            return keyword.title()
    return None


# State Extraction

def _extract_state(text: str):
    text_lower = text.lower()
    for state in INDIAN_STATES:
        if state in text_lower:
            return state.title()
    return None



 # gender Extraction

def _extract_gender(text):
    text_lower = text.lower()
    if re.search(r"\b(male|man|he)\b", text_lower):
        return "male"
    if re.search(r"\b(female|woman|she)\b", text_lower):
        return "female"
    return None


# Category Extraction

def _extract_category(text):
    text_lower = text.lower()
    for keyword , label in CATEGORY_KEYWORDS.items():
        if re.search(rf"\b{keyword}\b" , text_lower):
            return label
    return None


# Final Profile OF A Human 

def extract_profile(transcript) ->dict :
    """
    Extracts a structured profile dict from a raw transcript using regex / keyword rules only 

    Returns the find fields and missing field in given transcript
    
    """
    profile = {
        "age": _extract_age(transcript),
        "income": _extract_income(transcript),
        "occupation": _extract_occupation(transcript),
        "state": _extract_state(transcript),
        "gender": _extract_gender(transcript),
        "category": _extract_category(transcript),
    }

    missing_fields = [f for f in REQUIRED_FIELDS if not profile.get(f)]

    return {
        "profile" : profile ,
        "missing_fields":missing_fields
    }


if __name__ == "__main__":

    sample_transcript = (
        "I am a 45 year old farmer from Rajasthan, my income is around 1.5 lakh rupees, I am male, general category."
    )


    result = extract_profile(sample_transcript)
    print(result)