"""食事記録API"""
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database import get_db
from src.models import User, MealLog, Menu
from src.schemas.meal_log import MealLogCreate, MealLogResponse, TodaySummary

router = APIRouter(prefix="/meal-logs", tags=["meal-logs"])


def _get_calories_and_price(session: Session, log: MealLog) -> tuple[int, int, str | None]:
    """MealLogからカロリー・価格・メニュー名を取得"""
    if log.menu_id:
        menu = session.get(Menu, log.menu_id)
        if menu:
            return menu.calories, menu.price, menu.menu_name
    return (
        log.manual_calories or 0,
        log.manual_price or 0,
        None,
    )


@router.post("/users/{user_id}", response_model=MealLogResponse)
def create_meal_log(
    user_id: int,
    data: MealLogCreate,
    session: Session = Depends(get_db),
):
    """食事記録を追加"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if data.menu_id and (data.manual_calories is not None or data.manual_price is not None):
        raise HTTPException(400, "menu_id指定時はmanual_calories/priceは不要")
    if not data.menu_id and (data.manual_calories is None or data.manual_price is None):
        raise HTTPException(400, "非チェーン時はmanual_caloriesとmanual_priceが必須")

    eaten_at = data.eaten_at or datetime.now()
    log = MealLog(
        user_id=user_id,
        menu_id=data.menu_id,
        eaten_at=eaten_at,
        manual_calories=data.manual_calories,
        manual_price=data.manual_price,
        manual_protein=data.manual_protein,
        manual_fat=data.manual_fat,
        manual_carbs=data.manual_carbs,
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    cal, price, name = _get_calories_and_price(session, log)
    return MealLogResponse(
        log_id=log.log_id,
        user_id=log.user_id,
        menu_id=log.menu_id,
        eaten_at=log.eaten_at,
        calories=cal,
        price=price,
        menu_name=name,
    )


@router.get("/users/{user_id}/today", response_model=TodaySummary)
def get_today_summary(user_id: int, session: Session = Depends(get_db)):
    """本日の食事サマリー（残り予算・カロリー）"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    today = date.today()
    logs = (
        session.query(MealLog)
        .filter(
            MealLog.user_id == user_id,
            func.date(MealLog.eaten_at) == today,
        )
        .all()
    )

    total_cal = 0
    total_price = 0
    for log in logs:
        cal, price, _ = _get_calories_and_price(session, log)
        total_cal += cal
        total_price += price

    return TodaySummary(
        total_calories=total_cal,
        total_price=total_price,
        remaining_calories=max(0, user.daily_calorie_limit - total_cal),
        remaining_budget=max(0, user.daily_budget_limit - total_price),
        meal_count=len(logs),
    )
