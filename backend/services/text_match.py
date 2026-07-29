"""
text_match.py

Matches against name + brand + quantity combined (not name alone),
and splits the query into words so each word just needs to appear
somewhere in that combined text — order-independent, so "milk 2 L"
matches a product named "Semi-Skimmed Milk" with quantity "2 l".
"""


def matches_query(product: dict, query: str) -> bool:
    """True if every word in the query appears somewhere in the product's name, brand, or quantity."""
    words = query.strip().lower().split()
    if not words:
        return False

    haystack = " ".join([
        product.get("name", ""),
        product.get("brand", ""),
        product.get("quantity", ""),
    ]).lower()

    return all(word in haystack for word in words)
