# BasketWise

An AI shopping decision assistant — not just another list app.

Built for the algo1 Graduate Product Engineer technical case study.

## The problem

Existing grocery tools each solve one narrow piece: list apps organize,
comparison tools (Shopsplit) compare cross-retailer prices, allergen tools
(LiberEat) filter safety. Nobody combines cross-retailer awareness, live
in-store use, and active decision-load reduction. BasketWise's core thesis:
every feature should remove a decision from the shopper, not just organize
or display more information.

Full research, persona, and architecture reasoning: see `docs/research.md`
and `docs/architecture-notes.md`.

## Features

- **Structured personaliser** — guided allergen/dietary/budget intake
- **Cross-retailer search** — Tesco, Sainsbury's, Aldi, or All
- **Safety filter** — hard exclusion of allergen/diet conflicts, always
  re-applied server-side on every recommendation, never trusted from cache
- **Budget-aware ranking** — weighting shifts toward price as remaining
  budget tightens
- **AI recommendation justification** — one-line reasoning per pick, via
  AWS Bedrock (Claude Haiku 4.5), with a rule-based fallback if the AI
  call fails
- **Quantity assistant** — opt-in, AI-powered "how much do I need"
- **Meal-prompt** — "vegetarian curry for 4" auto-populates a full,
  safety-filtered, budget-aware shopping list using the same underlying
  recommendation engine as manual search
- **Live budget tracker** — running total, feeds back into ranking

## Architecture

```
frontend/          Vanilla HTML/CSS/JS — no build step, no framework
backend/            FastAPI
├── routes/         /filter, /recommend, /search, /quantity, /meal-plan
├── services/        filter_products.py, rank_products.py, llm_client.py
├── models/          Pydantic schemas
└── data/            products.json (90 mock products)
```

**AI does judgement, not retrieval.** Safety filtering and budget/rating
ranking are deterministic and auditable. AI (AWS Bedrock) is reserved for
natural language tasks: the personaliser conversation, meal-prompt
ingredient extraction, one-line recommendation justification, and
quantity suggestions. Every Bedrock call has a graceful fallback to
rule-based logic — an AI failure never breaks the app.

## Data

Product allergen, dietary label, and ingredient data is sourced from
[Open Food Facts](https://world.openfoodfacts.org), used under the Open
Database License (ODbL). Retailer, price, rating, and offer fields are
manually curated, since no UK grocery retailer exposes a public product
or pricing API — this constraint, and the reasoning behind it, is
documented in `docs/architecture-notes.md`.

## Running locally

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create .env with AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BEDROCK_MODEL_ID
uvicorn main:app --reload
```
Runs at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

**Frontend:**
```bash
cd frontend
python3 -m http.server 5500
```
Open `http://localhost:5500` in a browser.

## Walkthrough

1. Landing page → "Get Started"
2. Personaliser → answer allergen/diet/budget questions → "Continue"
3. Confirmation popup shows what was filtered
4. Shop page → search an item (live suggestions as you type) or type a
   meal prompt (e.g. "vegetarian curry for 4")
5. Top recommendation shown with AI justification; alternatives below
6. Add items to list → budget tracker updates live

## What was deliberately scoped out, and why

See `docs/architecture-notes.md` for the full list (live retailer APIs,
real aisle navigation, full auth, pantry-to-recipe suggestions, etc.) —
each cut is a documented decision, not an oversight.

## Tech stack

Vanilla HTML/CSS/JS · FastAPI · Pydantic · AWS Bedrock (Claude Haiku 4.5) ·
Open Food Facts API

## Author

Bhoomi Bhat
