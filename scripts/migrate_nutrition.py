#!/usr/bin/env python3
"""栄養素カラム追加マイグレーション（SQLite用）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import engine
from sqlalchemy import text

def main():
    with engine.begin() as conn:
        cols = [r[1] for r in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
        if "gender" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR(10)"))
        if "birth_year" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN birth_year INTEGER"))

        cols = [r[1] for r in conn.execute(text("PRAGMA table_info(menus)")).fetchall()]
        for c in ["protein", "fat", "carbs"]:
            if c not in cols:
                conn.execute(text(f"ALTER TABLE menus ADD COLUMN {c} REAL"))

        cols = [r[1] for r in conn.execute(text("PRAGMA table_info(meal_logs)")).fetchall()]
        for c in ["manual_protein", "manual_fat", "manual_carbs"]:
            if c not in cols:
                conn.execute(text(f"ALTER TABLE meal_logs ADD COLUMN {c} REAL"))

    print("Migration done.")

if __name__ == "__main__":
    main()
