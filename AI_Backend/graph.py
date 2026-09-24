"""
graph.py
---------
Builds and runs the LangGraph workflow:
    parse_profile -> check_eligibility -> rank_schemes -> END
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END

from schema import WorkflowState
from nodes import parse_profile, check_eligibility, rank_schemes


def build_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("parse_profile", parse_profile)
    graph.add_node("check_eligibility", check_eligibility)
    graph.add_node("rank_schemes", rank_schemes)

    graph.set_entry_point("parse_profile")
    graph.add_edge("parse_profile", "check_eligibility")
    graph.add_edge("check_eligibility", "rank_schemes")
    graph.add_edge("rank_schemes", END)

    return graph.compile()


_compiled_graph = build_graph()


def run_recommendation_workflow(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point used by the rest of the app (main_flow.py, FastAPI main.py).
    Takes a structured profile and returns ranked scheme recommendations.
    """
    initial_state: WorkflowState = {
        "profile": profile,
        "eligible_schemes": [],
        "ranked_schemes": [],
    }
    result = _compiled_graph.invoke(initial_state)
    return {
        "eligible_count": len(result["ranked_schemes"]),
        "recommendations": result["ranked_schemes"],
    }


if __name__ == "__main__":
    # quick manual test
    sample_profile = {"age": 45, "income": 150000, "occupation": "farmer", "state": "Rajasthan"}
    result = run_recommendation_workflow(sample_profile)
    print(result)