"""
routes/search.py

Instant-suggestions endpoint, meant to run on every keystroke while the
user types. Deliberately does the least amount of work possible: a
plain word match (via text_match.matches_query — same matcher
/recommend uses, so "milk 2 L" finds the same products here as it
would in the real search), no safety filtering, no ranking, no AI
call. /recommend (not this endpoint) is what actually filters for
allergens and dietary preference — this one is just "what could I
mean", so it must stay fast and cheap.
"""

from fastapi import APIRouter

from services.data_loader import load_products
from services.text_match import matches_query

router = APIRouter()

MAX_RESULTS = 8


@router.get("/search")
def search(q: str = "", retailer: str = "All"):
    """Fast, unfiltered word match on name/brand/quantity — for typeahead only, not a safety-checked result."""
    if not q.strip():
        return []

    products = load_products()

    if retailer and retailer != "All":
        products = [p for p in products if p["retailer"] == retailer]

    matches = [p for p in products if matches_query(p, q)]

    return [
        {"id": p["id"], "name": p["name"], "brand": p["brand"], "retailer": p["retailer"], "quantity": p["quantity"]}
        for p in matches[:MAX_RESULTS]
    ]
