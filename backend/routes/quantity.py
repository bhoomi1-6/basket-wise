"""
routes/quantity.py

Suggests how much of an item to buy for a given context. If Bedrock is
unavailable, this returns an honest "can't suggest right now" message
rather than a crash or a made-up number — a wrong quantity is worse
than no quantity, so we never fabricate a fallback answer here.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from services.llm_client import generate_text

router = APIRouter()

FALLBACK_MESSAGE = "Unable to generate a suggestion right now — please enter a quantity manually."


class QuantityRequest(BaseModel):
    item: str
    context: str


class QuantityResponse(BaseModel):
    suggestion: str


def build_quantity_prompt(item: str, context: str) -> str:
    """One constrained ask: a quantity plus a brief reason, nothing else."""
    return (
        "You are a shopping assistant. Suggest how much of this item to buy. "
        "Reply in ONE short sentence: a quantity followed by a brief reason. "
        f"Item: {item}. Context: {context}. "
        'Example format: "About 600g — roughly 150g per person for a main course."'
    )


@router.post("/quantity", response_model=QuantityResponse)
def suggest_quantity(request: QuantityRequest) -> QuantityResponse:
    """Returns an AI quantity suggestion, or a graceful fallback message if Bedrock is unavailable."""
    prompt = build_quantity_prompt(request.item, request.context)
    suggestion = generate_text(prompt, max_tokens=60)

    return QuantityResponse(suggestion=suggestion or FALLBACK_MESSAGE)
