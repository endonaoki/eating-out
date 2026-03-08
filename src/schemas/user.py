"""User スキーマ"""
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    daily_calorie_limit: int = Field(2000, ge=500, le=5000)
    daily_budget_limit: int = Field(1500, ge=0, le=50000)


class UserUpdate(BaseModel):
    daily_calorie_limit: int | None = Field(None, ge=500, le=5000)
    daily_budget_limit: int | None = Field(None, ge=0, le=50000)


class UserResponse(BaseModel):
    user_id: int
    daily_calorie_limit: int
    daily_budget_limit: int

    class Config:
        from_attributes = True
