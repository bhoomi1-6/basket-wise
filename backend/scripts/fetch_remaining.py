"""
fetch_data.py

Fetches real UK grocery product data (allergens, dietary labels, brand,
name, quantity) from the Open Food Facts API across 10 categories,
9 products each = 90 products total.

Price, rating, retailer, and offer are NOT available from Open Food
Facts — those come back as null/None here. Use enrich_dataset.py
afterward to fill them in via a spreadsheet.

Usage:
    pip install requests
    python3 fetch_data.py

Output:
    products_openfoodfacts.json
"""

import json
import time
import requests

BASE_URL = "https://world.openfoodfacts.org/api/v2/search"

HEADERS = {
    "User-Agent": "BasketWise/1.0 (product case study; contact: bhoomibhat753@gmail.com)"
}

# 10 categories x 9 products = 90 total.
# Using structured category tags (not free-text search) — reliable,
# correctly-matched results. Browse tags at openfoodfacts.org/categories
CATEGORIES = {
    "breads":   "Bakery",
    "eggs":     "Dairy",
    "yogurts":  "Dairy",

}

FIELDS = ",".join([
    "product_name",
    "brands",
    "allergens_tags",
    "traces_tags",
    "labels_tags",
    "nutriscore_grade",
    "quantity",
])

PAGE_SIZE = 9  # 10 categories x 9 = 90 products


def clean_tags(tags):
    """Strip Open Food Facts' 'en:' prefix and format for readability."""
    if not tags:
        return []
    return sorted({t.replace("en:", "").replace("-", " ") for t in tags})


def fetch_for_category(category_tag, category_label, max_retries=3):
    """Query Open Food Facts for one category, UK products only. Retries on 503."""
    params = {
        "categories_tags": category_tag,
        "countries_tags": "united-kingdom",
        "fields": FIELDS,
        "page_size": PAGE_SIZE,
        "json": 1,
    }

    for attempt in range(1, max_retries + 1):
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
        if resp.status_code == 503:
            wait = attempt * 3  # 3s, 6s, 9s
            print(f"  503 (server busy) — retrying in {wait}s (attempt {attempt}/{max_retries})...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        break
    else:
        print(f"  Gave up on '{category_tag}' after {max_retries} retries.")
        return []

    products = []
    for i, item in enumerate(data.get("products", [])):
        name = item.get("product_name")
        if not name:
            continue  # skip entries with no usable name

        products.append({
            "id": f"{category_tag}-{i}",
            "name": name.strip(),
            "brand": item.get("brands", "Unknown").split(",")[0].strip(),
            "category": category_label,
            "quantity": item.get("quantity", ""),
            "allergens": clean_tags(item.get("allergens_tags")),
            "traces": clean_tags(item.get("traces_tags")),
            "dietaryLabels": clean_tags(item.get("labels_tags")),
            "nutriScore": (item.get("nutriscore_grade") or "").upper() or None,
            # --- Not available from Open Food Facts, fill in via enrich_dataset.py ---
            "retailer": None,
            "price": None,
            "rating": None,
            "offer": None,
        })
    return products


def main():
    all_products = []

    for category_tag, category_label in CATEGORIES.items():
        print(f"Fetching '{category_tag}' ({category_label})...")
        products = fetch_for_category(category_tag, category_label)
        print(f"  Got {len(products)} products")
        all_products.extend(products)
        time.sleep(3)  # be polite to the free API — avoid triggering 503s

    out_path = "products_remaining.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_products)} products to {out_path}")
    print("Next: run enrich_dataset.py to fill in retailer, price, rating, offer.")


if __name__ == "__main__":
    main()