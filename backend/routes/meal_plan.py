"""
routes/meal_plan.py

Turns a dish into an ingredient list, then hands each ingredient
straight to the existing /recommend engine. This file's only job is
"dish -> ingredients" — it deliberately does not touch filtering,
ranking, or justification itself, so there's exactly one place
(routes/recommend.py) that owns product safety logic.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from models.schemas import UserProfile, RecommendRequest, RecommendResponse
from services.llm_client import generate_text
from routes.recommend import run_recommendation

router = APIRouter()

# Used as remainingBudget for each per-ingredient /recommend call, since
# a meal plan has no single "remaining budget" concept of its own yet.
DEFAULT_INGREDIENT_BUDGET = 10.0


class MealPlanRequest(BaseModel):
    dish: str
    profile: UserProfile


class MealPlanResponse(BaseModel):
    ingredients: list[str]
    recommendations: list[RecommendResponse]
    message: str | None = None


def build_meal_plan_prompt(dish: str) -> str:
    """One constrained ask: a bare comma-separated ingredient list, nothing else."""
    return (
        "You are a shopping assistant. List the ingredients needed for this dish "
        "as a single comma-separated line — no recipe steps, no quantities, no "
        "extra text, just ingredient names. "
        f"Dish: {dish}. "
        'Example format: "onion, garlic, chickpeas, coconut milk, rice, curry powder"'
    )


@router.post("/meal-plan", response_model=MealPlanResponse)
def meal_plan(request: MealPlanRequest) -> MealPlanResponse:
    """
    If Bedrock is unavailable, returns a 200 with an empty ingredient
    list and an explanatory message rather than erroring — a meal plan
    that can't be generated yet is a normal, expected state for the
    frontend to show, not a server failure.
    """
    prompt = build_meal_plan_prompt(request.dish)
    ai_text = generate_text(prompt, max_tokens=100)

    if not ai_text:
        return MealPlanResponse(
            ingredients=[],
            recommendations=[],
            message="AI meal planning is temporarily unavailable — please try again shortly.",
        )

    ingredients = [item.strip() for item in ai_text.split(",") if item.strip()]

    recommendations = [
        run_recommendation(
            RecommendRequest(
                searchTerm=ingredient,
                profile=request.profile,
                remainingBudget=DEFAULT_INGREDIENT_BUDGET,
            )
        )
        for ingredient in ingredients
    ]

    return MealPlanResponse(ingredients=ingredients, recommendations=recommendations)
