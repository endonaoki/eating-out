"""User モデル"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    daily_calorie_limit: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    daily_budget_limit: Mapped[int] = mapped_column(Integer, default=1500, nullable=False)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)  # male, female, other
    birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 生年

    meal_logs: Mapped[list["MealLog"]] = relationship("MealLog", back_populates="user")
