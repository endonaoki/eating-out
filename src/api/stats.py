"""栄養・健康バランス統計API"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database import get_db
from src.models import User, MealLog, Menu

router = APIRouter(prefix="/stats", tags=["stats"])


def _get_nutrition(session: Session, log: MealLog) -> dict:
    base = {}
    if log.menu_id:
        m = session.get(Menu, log.menu_id)
        if m:
            base = {
                "calories": m.calories,
                "protein": float(m.protein or 0),
                "fat": float(m.fat or 0),
                "carbs": float(m.carbs or 0),
            }
    else:
        base = {
            "calories": log.manual_calories or 0,
            "protein": float(log.manual_protein or 0),
            "fat": float(log.manual_fat or 0),
            "carbs": float(log.manual_carbs or 0),
        }
    # 鉄・カルシウム・ビタミンCの推定（タンパク質・脂質・炭水化物から簡易計算）
    p, f, c = base["protein"], base["fat"], base["carbs"]
    base["iron"] = p * 0.15 + c * 0.02  # 肉・穀物由来の推定
    base["calcium"] = p * 5 + f * 2  # 乳製品・魚由来の推定
    base["vitamin_c"] = c * 0.5  # 野菜・果物由来の推定
    return base


@router.get("/users/{user_id}")
def get_stats(
    user_id: int,
    period: str = Query("day", description="day, week, month, year"),
    session: Session = Depends(get_db),
):
    """期間別の栄養・カロリー統計"""
    user = session.get(User, user_id)
    if not user:
        return {"error": "User not found"}

    today = date.today()
    if period == "day":
        start = today
        end = today
    elif period == "week":
        start = today - timedelta(days=6)
        end = today
    elif period == "month":
        start = today - timedelta(days=29)
        end = today
    elif period == "year":
        start = today - timedelta(days=364)
        end = today
    else:
        start, end = today, today

    logs = (
        session.query(MealLog)
        .filter(
            MealLog.user_id == user_id,
            func.date(MealLog.eaten_at) >= start,
            func.date(MealLog.eaten_at) <= end,
        )
        .all()
    )

    total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "iron": 0, "calcium": 0, "vitamin_c": 0, "price": 0}
    for log in logs:
        n = _get_nutrition(session, log)
        total["calories"] += n["calories"]
        total["protein"] += n["protein"]
        total["fat"] += n["fat"]
        total["carbs"] += n["carbs"]
        total["iron"] += n.get("iron", 0)
        total["calcium"] += n.get("calcium", 0)
        total["vitamin_c"] += n.get("vitamin_c", 0)
        if log.menu_id:
            m = session.get(Menu, log.menu_id)
            total["price"] += m.price if m else 0
        else:
            total["price"] += log.manual_price or 0

    # 推奨値（簡易: 年齢・性別は将来拡張）
    age = (today.year - user.birth_year) if user.birth_year else 35
    base_cal = 2000 if (user.gender or "").lower() != "female" else 1800
    # 年齢補正: 30歳以上で-50/10歳
    if age >= 30:
        base_cal -= (age - 30) // 10 * 50
    rec_protein = base_cal * 0.2 / 4  # 20% from protein
    rec_fat = base_cal * 0.25 / 9
    rec_carbs = base_cal * 0.55 / 4

    days = (end - start).days + 1
    return {
        "period": period,
        "start": str(start),
        "end": str(end),
        "days": days,
        "totals": total,
        "averages": {
            "calories": round(total["calories"] / days, 1),
            "protein": round(total["protein"] / days, 1),
            "fat": round(total["fat"] / days, 1),
            "carbs": round(total["carbs"] / days, 1),
            "price": round(total["price"] / days, 0),
        },
        "recommended_daily": {
            "calories": base_cal,
            "protein": round(rec_protein, 1),
            "fat": round(rec_fat, 1),
            "carbs": round(rec_carbs, 1),
            "iron": 10,
            "calcium": 700,
            "vitamin_c": 100,
        },
        "meal_count": len(logs),
    }
