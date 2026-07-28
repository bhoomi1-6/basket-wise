import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")

def load_products():
    """
    Single source of truth for reading the product catalog. Both /filter
    and /recommend call this independently on every request. No caching is done
    since products.json is small and the catalog is expected to change frequently.
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)