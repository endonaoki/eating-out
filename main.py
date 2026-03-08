"""Eating Out API エントリーポイント"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import init_db
from src.api.chains import router as chains_router
from src.api.users import router as users_router
from src.api.meal_logs import router as meal_logs_router
from src.api.recommend import router as recommend_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """起動時にDB初期化"""
    init_db()
    yield
    # シャットダウン処理（必要に応じて）


app = FastAPI(
    title="Eating Out API",
    description="外食特化 食事管理アプリのバックエンドAPI",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(chains_router)
app.include_router(users_router)
app.include_router(meal_logs_router)
app.include_router(recommend_router)


@app.get("/")
def root():
    return {"message": "Eating Out API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
