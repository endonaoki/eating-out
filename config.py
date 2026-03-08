"""アプリケーション設定"""
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# プロジェクトルート
BASE_DIR = Path(__file__).resolve().parent

# データベース
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'data' / 'eating_out.db'}"
)
