"""
filter_products.py

Safety-critical hard filter: removes any product that conflicts with the
user's allergen or dietary profile. This ALWAYS runs before ranking
ranking should only ever operate on products that have already passed
through here.
"""

from typing import List, Dict, Any


def _normalize(value: str) -> str:
    """Lowercase and strip for consistent, case-insensitive matching."""
    return value.strip().lower()


def _has_allergen_conflict(product: Dict[str, Any], user_allergens: List[str]) -> bool:
    """
    True if the product's declared allergens OR trace warnings ("may
    contain") intersect with anything the user needs to avoid.

    Traces are included deliberately — a "may contain nuts" warning is
    still unsafe for someone with a nut allergy, even though it's a
    lower-confidence label than a direct declared allergen.
    """
    if not user_allergens:
        return False

    user_set = {_normalize(a) for a in user_allergens}
    product_allergens = {_normalize(a) for a in product.get("allergens", [])}
    product_traces = {_normalize(t) for t in product.get("traces", [])}

    return bool(user_set & (product_allergens | product_traces))


def _matches_dietary_preference(product: Dict[str, Any], preference: str) -> bool:
    """
    True if the product satisfies the user's stated dietary preference.
    'none' / None always passes. Vegan products also satisfy a
    vegetarian preference (vegan is a strict subset), but not the
    reverse.
    """
    if not preference or _normalize(preference) == "none":
        return True

    pref = _normalize(preference)
    labels = {_normalize(label) for label in product.get("dietaryLabels", [])}

    if pref == "vegan":
        return "vegan" in labels
    if pref == "vegetarian":
        return "vegetarian" in labels or "vegan" in labels

    # Unrecognized/custom preference (e.g. "other") — don't block on it,
    # since we can't confidently evaluate it against the label set.
    return True


def filter_products(
    products: List[Dict[str, Any]],
    user_allergens: List[str],
    dietary_preference: str = None,
) -> List[Dict[str, Any]]:
    """
    Returns only the products that are safe for the given profile.

    This is the single gate every product must pass through before it
    can be ranked or recommended.
    """
    safe_products = []

    for product in products:
        if _has_allergen_conflict(product, user_allergens):
            continue
        if not _matches_dietary_preference(product, dietary_preference):
            continue
        safe_products.append(product)

    return safe_products


