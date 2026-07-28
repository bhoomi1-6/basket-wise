"""
rank_products.py

Ranks an already-safety-filtered set of products by rating and price,
dynamically weighting the two based on how much budget the user has
left. This should only ever be called AFTER filter_products.py — it
assumes every product it receives is already safe to recommend.

Design intent (see architecture notes): early in a shop, with plenty
of budget left, rating is weighted more heavily — no pressure yet,
recommend the better product. As remaining budget tightens relative to
typical prices in the candidate set, price is weighted more heavily —
steering toward the cheapest safe option that still meets the need.
"""

from typing import List, Dict, Any


def _normalize_range(value: float, min_val: float, max_val: float) -> float:
    """
    Scales a value to a 0-1 range given the min/max of its candidate
    set. Returns 0.5 (neutral) if all candidates are identical, to
    avoid a divide-by-zero and avoid arbitrarily favouring one product
    when there's nothing to differentiate them on.
    """
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def _budget_pressure(remaining_budget: float, candidate_prices: List[float]) -> float:
    """
    Returns a 0-1 "pressure" score: how tight the remaining budget is
    relative to what's actually on offer in this candidate set.

    0   = plenty of headroom (remaining budget comfortably covers even
          the most expensive candidate several times over)
    1   = very tight (remaining budget barely covers the cheapest
          candidate, or is already exhausted)
    """
    if not candidate_prices:
        return 0.5

    avg_price = sum(candidate_prices) / len(candidate_prices)

    if remaining_budget <= 0:
        return 1.0

    ratio = avg_price / remaining_budget
    return max(0.0, min(1.0, ratio))


def compute_weights(remaining_budget: float, prices: List[float]) -> tuple:
    """
    Returns (rating_weight, price_weight) for a candidate set, given how
    much budget is left. Pulled out of rank_products so callers that need
    to know *why* the ranking leaned rating- or price-first (e.g. the
    justification text) can ask for the same weights without duplicating
    the budget-pressure math.

    Budget pressure directly sets the weighting split:
    Low pressure (0.0)  -> rating weighted 0.7, price weighted 0.3
    High pressure (1.0) -> rating weighted 0.3, price weighted 0.7
    """
    pressure = _budget_pressure(remaining_budget, prices)
    rating_weight = 0.7 - (0.4 * pressure)
    price_weight = 1.0 - rating_weight
    return rating_weight, price_weight


def rank_products(
    products: List[Dict[str, Any]],
    remaining_budget: float,
) -> List[Dict[str, Any]]:
    """
    Returns the products sorted best-first. The first item is the top
    recommendation; the rest are the demoted "alternatives" shown
    smaller in the UI.

    Assumes `products` is already the safety-filtered set — this
    function does not re-check allergens or dietary labels.
    """
    if not products:
        return []

    ratings = [p["rating"] for p in products]
    prices = [p["price"] for p in products]

    min_rating, max_rating = min(ratings), max(ratings)
    min_price, max_price = min(prices), max(prices)

    rating_weight, price_weight = compute_weights(remaining_budget, prices)

    def score(product: Dict[str, Any]) -> float:
        rating_score = _normalize_range(product["rating"], min_rating, max_rating)
        # Price is inverted — a LOWER price should score HIGHER.
        price_score = 1.0 - _normalize_range(product["price"], min_price, max_price)
        return (rating_score * rating_weight) + (price_score * price_weight)

    ranked = sorted(products, key=score, reverse=True)
    return ranked
