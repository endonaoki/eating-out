"""User モデル"""
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    daily_calorie_limit: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    daily_budget_limit: Mapped[int] = mapped_column(Integer, default=1500, nullable=False)

    meal_logs: Mapped[list["MealLog"]] = relationship("MealLog", back_populates="user")
