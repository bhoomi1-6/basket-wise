"""
routes/filter.py

UX-only endpoint: after the personaliser step, tells the user how many
of the full catalog are safe for them before they start searching. It
intentionally doesn't persist or cache anything for /recommend to
reuse — /recommend re-derives its own safe set from scratch so the two
endpoints can never drift out of sync.
"""

from fastapi import APIRouter

from models.schemas import FilterRequest, FilterResponse
from services.data_loader import load_products
from services.filter_products import filter_products

router = APIRouter()


@router.post("/filter", response_model=FilterResponse)
def filter_catalog(request: FilterRequest) -> FilterResponse:
    """Reports how much of the full catalog is safe for this profile."""
    products = load_products()
    safe_products = filter_products(
        products,
        request.profile.allergens,
        request.profile.dietaryPreference,
    )

    safe_count = len(safe_products)
    total_count = len(products)

    return FilterResponse(
        safeCount=safe_count,
        excludedCount=total_count - safe_count,
        excludedAllergens=request.profile.allergens,
    )
