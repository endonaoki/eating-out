#!/usr/bin/env python3
"""既存メニューに栄養素を推定で追加"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import get_session
from src.models import Menu

# カロリーから推定: P:C:F = 約 20:50:30 の比率（一般的な外食）
def estimate_nutrition(calories: int) -> tuple[float, float, float]:
    # protein 4kcal/g, carbs 4kcal/g, fat 9kcal/g
    # 例: 600kcal -> P60g, C75g, F20g 程度
    p_ratio, c_ratio, f_ratio = 0.2, 0.5, 0.3
    p_cal = calories * p_ratio
    c_cal = calories * c_ratio
    f_cal = calories * f_ratio
    protein = p_cal / 4
    carbs = c_cal / 4
    fat = f_cal / 9
    return round(protein, 1), round(carbs, 1), round(fat, 1)

def main():
    session = get_session()
    menus = session.query(Menu).all()
    for m in menus:
        if m.protein is None and m.calories:
            p, c, f = estimate_nutrition(m.calories)
            m.protein = p
            m.fat = f
            m.carbs = c
    session.commit()
    session.close()
    print(f"Updated {len(menus)} menus with nutrition estimates.")

if __name__ == "__main__":
    main()
