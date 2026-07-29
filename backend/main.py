from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.filter import router as filter_router
from routes.recommend import router as recommend_router
from routes.quantity import router as quantity_router
from routes.meal_plan import router as meal_plan_router
from routes.search import router as search_router

app = FastAPI(title="BasketWise API")

# Demo app, not production — every origin is allowed so the static
# frontend can be opened straight from the filesystem or any port
# without CORS friction.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filter_router)
app.include_router(recommend_router)
app.include_router(quantity_router)
app.include_router(meal_plan_router)
app.include_router(search_router)

@app.get("/")
def health():
    return {"status": "ok"}