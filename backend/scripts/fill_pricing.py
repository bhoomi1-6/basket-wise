"""
Fill retailer / price / rating / offer for products.json.
Values are hand-set per product based on typical UK Tesco/Aldi/Sainsbury's
shelf prices for that item and pack size (manual research, not an API).
Only these four fields are touched — everything else is left as-is.
"""

import json

DATA_PATH = "/Users/bhoomibhat/Documents/Algo1/basket-wise/backend/data/products.json"

# id -> (retailer, price, rating, offer)
FILL = {
    # creams
    "creams-0": ("Tesco", 1.60, 4.2, None),
    "creams-1": ("Sainsbury's", 5.50, 4.6, None),
    "creams-2": ("Tesco", 1.40, 4.1, None),
    "creams-3": ("Sainsbury's", 1.95, 3.9, None),
    "creams-4": ("Tesco", 1.30, 4.0, None),
    "creams-5": ("Aldi", 0.89, 4.4, None),
    "creams-6": ("Sainsbury's", 1.50, 4.3, "2 for £2.50"),
    "creams-7": ("Aldi", 1.85, 4.5, None),
    "creams-8": ("Tesco", 1.35, 4.0, None),

    # milks
    "milks-0": ("Tesco", 1.65, 4.3, None),
    "milks-1": ("Tesco", 1.65, 4.2, None),
    "milks-2": ("Sainsbury's", 1.65, 4.2, None),
    "milks-3": ("Aldi", 1.90, 4.4, None),
    "milks-4": ("Aldi", 1.45, 4.1, None),
    "milks-5": ("Tesco", 0.95, 4.2, None),
    "milks-6": ("Sainsbury's", 2.20, 4.5, None),
    "milks-7": ("Aldi", 1.55, 4.3, None),
    "milks-8": ("Sainsbury's", 3.20, 4.0, None),

    # cheeses
    "cheeses-0": ("Tesco", 1.90, 4.4, None),
    "cheeses-1": ("Sainsbury's", 2.10, 4.5, None),
    "cheeses-2": ("Tesco", 1.60, 4.1, "2 for £3"),
    "cheeses-3": ("Aldi", 3.20, 4.6, None),
    "cheeses-4": ("Sainsbury's", 2.75, 4.5, None),
    "cheeses-5": ("Aldi", 2.00, 4.3, None),
    "cheeses-6": ("Aldi", 1.35, 4.2, None),
    "cheeses-7": ("Sainsbury's", 1.85, 4.0, None),
    "cheeses-8": ("Aldi", 1.10, 3.8, None),

    # pastas
    "pastas-0": ("Sainsbury's", 2.75, 4.5, None),
    "pastas-1": ("Tesco", 1.55, 4.2, None),
    "pastas-2": ("Tesco", 0.95, 3.9, "3 for £2.50"),
    "pastas-3": ("Tesco", 2.50, 4.3, None),
    "pastas-4": ("Aldi", 0.65, 3.8, None),
    "pastas-5": ("Sainsbury's", 2.60, 4.2, None),
    "pastas-6": ("Tesco", 1.10, 4.1, None),
    "pastas-7": ("Aldi", 0.85, 4.0, None),
    "pastas-8": ("Sainsbury's", 1.75, 4.4, None),

    # rices
    "rices-0": ("Sainsbury's", 2.20, 4.3, None),
    "rices-1": ("Tesco", 1.90, 4.5, None),
    "rices-2": ("Aldi", 1.10, 3.9, None),
    "rices-3": ("Aldi", 0.95, 3.8, None),
    "rices-4": ("Tesco", 1.40, 4.2, None),
    "rices-5": ("Sainsbury's", 1.30, 4.1, None),
    "rices-6": ("Sainsbury's", 2.30, 4.5, "Save 15%"),
    "rices-7": ("Tesco", 0.85, 4.0, None),
    "rices-8": ("Aldi", 0.75, 3.9, None),

    # chickens
    "chickens-0": ("Tesco", 4.50, 4.4, None),
    "chickens-1": ("Tesco", 2.00, 4.3, None),
    "chickens-2": ("Sainsbury's", 2.25, 4.2, None),
    "chickens-3": ("Tesco", 1.75, 4.1, "2 for £3"),
    "chickens-4": ("Aldi", 1.65, 3.9, None),
    "chickens-5": ("Sainsbury's", 2.75, 4.3, None),
    "chickens-6": ("Tesco", 2.10, 4.2, None),
    "chickens-7": ("Aldi", 3.20, 4.5, None),
    "chickens-8": ("Tesco", 2.30, 4.4, None),

    # butters
    "butters-0": ("Tesco", 3.20, 4.5, None),
    "butters-1": ("Sainsbury's", 3.50, 4.2, None),
    "butters-2": ("Aldi", 3.00, 4.3, None),
    "butters-3": ("Aldi", 1.95, 3.9, None),
    "butters-4": ("Aldi", 1.85, 3.8, None),
    "butters-5": ("Tesco", 2.60, 4.4, None),
    "butters-6": ("Sainsbury's", 3.30, 4.5, "Clubcard Price £2.75"),
    "butters-7": ("Tesco", 2.10, 4.3, None),
    "butters-8": ("Tesco", 1.75, 4.1, None),

    # breads
    "breads-0": ("Sainsbury's", 1.80, 4.4, None),
    "breads-1": ("Sainsbury's", 1.90, 4.5, None),
    "breads-2": ("Aldi", 1.60, 4.3, None),
    "breads-3": ("Aldi", 1.55, 4.6, None),
    "breads-4": ("Sainsbury's", 1.70, 4.2, None),
    "breads-5": ("Aldi", 0.85, 3.9, "2 for £1.50"),
    "breads-6": ("Tesco", 2.20, 4.4, None),
    "breads-7": ("Tesco", 1.25, 4.3, None),
    "breads-8": ("Tesco", 2.00, 4.5, None),

    # eggs
    "eggs-0": ("Tesco", 3.15, 4.6, None),
    "eggs-1": ("Sainsbury's", 2.00, 4.0, None),
    "eggs-2": ("Aldi", 2.65, 4.4, None),
    "eggs-3": ("Aldi", 3.10, 4.3, None),
    "eggs-4": ("Sainsbury's", 3.50, 4.5, None),
    "eggs-5": ("Sainsbury's", 2.95, 4.4, None),
    "eggs-6": ("Aldi", 2.10, 4.1, "Save 20%"),
    "eggs-7": ("Tesco", 1.75, 3.9, None),
    "eggs-8": ("Sainsbury's", 1.70, 4.3, None),

    # yogurts
    "yogurts-0": ("Aldi", 1.85, 4.4, None),
    "yogurts-1": ("Sainsbury's", 3.20, 4.2, None),
    "yogurts-2": ("Tesco", 2.60, 4.6, None),
    "yogurts-3": ("Tesco", 2.60, 4.5, "2 for £4.50"),
    "yogurts-4": ("Aldi", 1.29, 4.3, None),
    "yogurts-5": ("Sainsbury's", 2.30, 4.4, None),
    "yogurts-6": ("Aldi", 1.35, 4.2, None),
    "yogurts-7": ("Sainsbury's", 4.00, 4.6, None),
    "yogurts-8": ("Tesco", 2.75, 4.5, None),
}


def main():
    with open(DATA_PATH) as f:
        products = json.load(f)

    missing = [p["id"] for p in products if p["id"] not in FILL]
    if missing:
        raise SystemExit(f"Missing fill data for: {missing}")

    for product in products:
        retailer, price, rating, offer = FILL[product["id"]]
        product["retailer"] = retailer
        product["price"] = price
        product["rating"] = rating
        product["offer"] = offer

    with open(DATA_PATH, "w") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
        f.write("\n")

    offers = sum(1 for p in products if p["offer"])
    counts = {}
    for p in products:
        counts[p["retailer"]] = counts.get(p["retailer"], 0) + 1
    print(f"Updated {len(products)} products.")
    print(f"Retailer distribution: {counts}")
    print(f"Products with an offer: {offers}")


if __name__ == "__main__":
    main()
