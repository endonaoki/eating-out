"""DB接続・セッション管理"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import DATABASE_URL
from src.models import Base

# SQLite用: ディレクトリを自動作成
if "sqlite" in DATABASE_URL:
    db_path = DATABASE_URL.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """テーブル作成"""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """セッション取得（コンテキストマネージャ）"""
    return SessionLocal()


def get_db():
    """FastAPI用 依存性注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
