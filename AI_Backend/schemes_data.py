"""
Sample scheme dataset — replace with data pulled from PostgreSQL /
PIB RSS feed (owned by the Database & Data Collection module).
"""

SCHEMES = [
    {
        "id": "PMKSY",
        "name": "PM Kisan Samman Nidhi",
        "description": "Income support for small and marginal farmers.",
        "eligibility_rules": {"min_age": 18, "max_age": 100, "max_income": 200000},
        "benefits": "₹6,000 per year in three installments.",
        "required_documents": ["Aadhaar Card", "Land Records", "Bank Passbook"],
        "priority_score": 9,
    },
    {
        "id": "PMAY",
        "name": "Pradhan Mantri Awas Yojana",
        "description": "Housing subsidy for economically weaker sections.",
        "eligibility_rules": {"min_age": 18, "max_age": 100, "max_income": 300000},
        "benefits": "Interest subsidy on home loans.",
        "required_documents": ["Aadhaar Card", "Income Certificate"],
        "priority_score": 8,
    },
    {
        "id": "SSY",
        "name": "Sukanya Samriddhi Yojana",
        "description": "Savings scheme for the girl child's future education/marriage.",
        "eligibility_rules": {"min_age": 0, "max_age": 10, "max_income": float("inf")},
        "benefits": "High interest savings account for girl children.",
        "required_documents": ["Birth Certificate", "Aadhaar Card"],
        "priority_score": 7,
    },
]