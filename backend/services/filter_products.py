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
    contain") intersect with anything the user needs to avoid, OR the
    thing to avoid literally appears in the product name.

    Traces are included deliberately — a "may contain nuts" warning is
    still unsafe for someone with a nut allergy, even though it's a
    lower-confidence label than a direct declared allergen.

    The name check exists for free-text "Other" entries like
    "tomatoes" — not a real allergen in Open Food Facts' standardized
    tag vocabulary, so a chip like "Milk"/"Gluten" is caught by the
    tags above, but a typed-in food avoidance never would be without
    also checking the name directly.
    """
    if not user_allergens:
        return False

    user_set = {_normalize(a) for a in user_allergens}
    product_allergens = {_normalize(a) for a in product.get("allergens", [])}
    product_traces = {_normalize(t) for t in product.get("traces", [])}

    if user_set & (product_allergens | product_traces):
        return True

    product_name = _normalize(product.get("name", ""))
    return any(_text_contains_term(product_name, allergen) for allergen in user_set)


def _text_contains_term(text: str, term: str) -> bool:
    """
    Substring match with basic singular/plural handling, so a typed
    "tomatoes" still catches a product named "Tomato & Basil" — plain
    substring matching alone misses that because they differ by more
    than just a trailing "s". Shared by the allergen name-check and
    the custom dietary-preference label-check below.
    """
    variants = {term}
    if term.endswith("es") and len(term) > 3:
        variants.add(term[:-2])  # tomatoes -> tomato
    if term.endswith("s") and len(term) > 3:
        variants.add(term[:-1])  # eggs -> egg

    return any(variant in text for variant in variants)


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

    # Custom/typed preference (e.g. "halal", "organic", "gluten free") —
    # not one of our two hardcoded values, so require it to appear
    # somewhere in the product's dietary labels. Previously any custom
    # preference passed every product through unfiltered, which meant
    # typing something like "halal" had no filtering effect at all.
    labels_text = " ".join(labels)
    return _text_contains_term(labels_text, pref)


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


