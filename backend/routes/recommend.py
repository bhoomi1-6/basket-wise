"""
routes/recommend.py

Search + safety-filter + rank, all in one request. The safety filter
is re-run here every single time on purpose — this endpoint must never
assume /filter already ran or that its result is still valid, since a
skipped or stale filter here is the one bug in this whole app that
could actually hurt someone.
"""

from fastapi import APIRouter

from models.schemas import RecommendRequest, RecommendResponse, Product
from services.data_loader import load_products
from services.filter_products import filter_products
from services.rank_products import rank_products, compute_weights
from services.justify import generate_justification
from services.llm_client import generate_text
from services.text_match import matches_query

router = APIRouter()


def build_justification_prompt(product: dict, favors: str, remaining_budget: float) -> str:
    """
    One clear, constrained ask: a single sentence, under 20 words,
    grounded in the actual product facts and in *why* the ranker
    picked it (rating-led vs. price-led) — kept separate from the
    calling code so it's easy to read and explain on its own.

    Remaining budget is passed in explicitly and the model is told to
    flag it if the price goes over — ranking can still surface an
    over-budget item when it's the only safe match, so the sentence
    shown to the user must never quietly hide that.
    """
    over_budget = product["price"] > remaining_budget
    budget_note = (
        f"This price is OVER the user's remaining budget of £{remaining_budget:.2f} — "
        "you MUST clearly say it exceeds the budget."
        if over_budget
        else f"This fits within the user's remaining budget of £{remaining_budget:.2f}."
    )
    return (
        "You are a shopping assistant. In ONE sentence, under 20 words, "
        "explain in a natural, human tone why this product was recommended. "
        f"Product: {product['name']} by {product['brand']}, sold at "
        f"{product['retailer']} for £{product['price']:.2f}, rated "
        f"{product['rating']}/5. The recommendation mainly favored "
        f"{favors}. {budget_note} Reply with only the sentence, no preamble."
    )


def get_justification(top_pick: dict, safe_matches: list, remaining_budget: float) -> str:
    """
    Tries Bedrock for a natural-language justification; if it's
    unavailable (generate_text returns None — timeout, bad creds,
    throttling, anything), silently falls back to the existing
    rule-based justification so the endpoint never returns a missing
    or broken explanation. Both paths are budget-aware — see
    build_justification_prompt and generate_justification.
    """
    prices = [p["price"] for p in safe_matches]
    rating_weight, price_weight = compute_weights(remaining_budget, prices)
    favors = "rating" if rating_weight >= price_weight else "price"

    prompt = build_justification_prompt(top_pick, favors, remaining_budget)
    ai_text = generate_text(prompt, max_tokens=60)

    if ai_text:
        return ai_text
    return generate_justification(top_pick, safe_matches, remaining_budget)


def run_recommendation(request: RecommendRequest) -> RecommendResponse:
    """
    The actual /recommend logic, pulled out from the route handler so
    other endpoints (e.g. /meal-plan) can call the exact same
    filter+rank+justify path per ingredient instead of reimplementing
    it — one recommendation engine, reused everywhere.
    """
    products = load_products()

    matches = [p for p in products if matches_query(p, request.searchTerm)]

    # Independent re-filter — never trust an earlier /filter call.
    safe_matches = filter_products(
        matches,
        request.profile.allergens,
        request.profile.dietaryPreference,
    )

    if not safe_matches:
        return RecommendResponse(topPick=None, justification=None, alternatives=[])

    ranked = rank_products(safe_matches, request.remainingBudget)
    top_pick, alternatives = ranked[0], ranked[1:]

    justification = get_justification(top_pick, safe_matches, request.remainingBudget)

    return RecommendResponse(
        topPick=Product(**top_pick),
        justification=justification,
        alternatives=[Product(**p) for p in alternatives],
    )


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    """Returns a ranked top pick + alternatives for a search term, or an empty result if nothing safe matches."""
    return run_recommendation(request)
