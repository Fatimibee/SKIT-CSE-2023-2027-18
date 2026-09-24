"""
---------
Individual node functions for the eligibility + recommendation workflow.
Each node takes the WorkflowState, updates it, and returns it.
"""

from schema import WorkflowState
from schemes_data import SCHEMES


def parse_profile(state: WorkflowState) -> WorkflowState:
    """Normalize/clean profile fields before eligibility checks."""
    profile = state["profile"]
    profile["income"] = profile.get("income") or 0
    profile["age"] = profile.get("age") or 0
    state["profile"] = profile
    return state


def check_eligibility(state: WorkflowState) -> WorkflowState:
    """Filter schemes the user is eligible for based on simple rule checks.
    Replace with LLM-based eligibility reasoning (Gemini) for complex criteria.
    """
    profile = state["profile"]
    eligible = []

    for scheme in SCHEMES:
        rules = scheme["eligibility_rules"]
        if profile["age"] < rules.get("min_age", 0):
            continue
        if profile["age"] > rules.get("max_age", 200):
            continue
        if profile["income"] > rules.get("max_income", float("inf")):
            continue
        eligible.append(scheme)

    state["eligible_schemes"] = eligible
    return state


def rank_schemes(state: WorkflowState) -> WorkflowState:
    """Rank eligible schemes — placeholder scoring, swap for LLM/embedding ranking."""
    ranked = sorted(
        state["eligible_schemes"],
        key=lambda s: s.get("priority_score", 0),
        reverse=True,
    )
    state["ranked_schemes"] = ranked
    return state