"""MealLog スキーマ"""
from datetime import datetime
from pydantic import BaseModel, Field


class MealLogCreate(BaseModel):
    menu_id: int | None = None
    eaten_at: datetime | None = None
    manual_calories: int | None = None
    manual_price: int | None = None
    manual_protein: float | None = None
    manual_fat: float | None = None
    manual_carbs: float | None = None


class MealLogResponse(BaseModel):
    log_id: int
    user_id: int
    menu_id: int | None
    eaten_at: datetime
    calories: int  # menuから取得 or manual
    price: int  # menuから取得 or manual
    menu_name: str | None  # チェーン時のみ

    class Config:
        from_attributes = True


class TodaySummary(BaseModel):
    total_calories: int
    total_price: int
    remaining_calories: int
    remaining_budget: int
    meal_count: int
