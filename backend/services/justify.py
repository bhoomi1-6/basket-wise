"""
justify.py

Generates the one-sentence explanation shown next to the top pick. Will move it to an 
LLM call once the frontend is connected for now it is a simple rule based engine for justification.
"""

from typing import List, Dict, Any

from services.rank_products import compute_weights


def generate_justification(
    top_pick: Dict[str, Any],
    products: List[Dict[str, Any]],
    remaining_budget: float,
) -> str:
    """
    Rule-based stand-in for an LLM explanation. Checked first: does the
    top pick actually fit what's left of the budget? Ranking never hard
    -excludes over-budget items (there may be no cheaper safe option),
    so the justification is the one place that must say so plainly —
    silently recommending something the user can't actually afford
    would be misleading, not "budget-aware".
    """
    if top_pick["price"] > remaining_budget:
        over_by = top_pick["price"] - remaining_budget
        return f"Best safe match, but £{over_by:.2f} over your remaining budget"

    prices = [p["price"] for p in products]
    rating_weight, price_weight = compute_weights(remaining_budget, prices)

    if rating_weight >= price_weight:
        return "Best-rated option within your budget"
    return "Cheapest safe match as your budget gets tight"
