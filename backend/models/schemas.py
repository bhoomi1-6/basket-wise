from pydantic import BaseModel
from typing import Optional, List

class Product(BaseModel):
    id: str
    name: str
    brand: str
    category: str
    quantity: str
    retailer: str
    price: float
    rating: float
    offer: Optional[str] = None
    allergens: List[str] = []
    traces: List[str] = []
    dietaryLabels: List[str] = []
    nutriScore: Optional[str] = None

class UserProfile(BaseModel):
    allergens: List[str] = []
    dietaryPreference: Optional[str] = None
    budget: float

class RecommendRequest(BaseModel):
    searchTerm: str
    profile: UserProfile
    remainingBudget: float

class RecommendResponse(BaseModel):
    # Optional: an empty safe-matches result is a valid outcome (e.g. every
    # product matching the search term conflicts with the user's profile),
    # not an error, so the frontend must be able to render "no match" state.
    topPick: Optional[Product] = None
    justification: Optional[str] = None
    alternatives: List[Product] = []

class FilterRequest(BaseModel):
    profile: UserProfile

class FilterResponse(BaseModel):
    safeCount: int
    excludedCount: int
    excludedAllergens: List[str]