"""MealLog モデル"""
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MealLog(Base):
    __tablename__ = "meal_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    menu_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("menus.menu_id"), nullable=True)
    eaten_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    manual_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manual_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="meal_logs")
