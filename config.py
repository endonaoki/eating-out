"""アプリケーション設定"""
import os
from pathlib import Path

# プロジェクトルート
BASE_DIR = Path(__file__).resolve().parent

# データベース
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'data' / 'eating_out.db'}"
)
