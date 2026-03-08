"""Eating Out API エントリーポイント"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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

# CORS（フロントエンド用）
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル（フロントエンド）
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(chains_router)
app.include_router(users_router)
app.include_router(meal_logs_router)
app.include_router(recommend_router)


@app.get("/")
def root():
    from fastapi.responses import FileResponse
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Eating Out API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
