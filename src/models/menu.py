"""Menu モデル"""
from sqlalchemy import Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Menu(Base, TimestampMixin):
    __tablename__ = "menus"

    menu_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chain_id: Mapped[int] = mapped_column(Integer, ForeignKey("chains.chain_id"), nullable=False)
    menu_name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    calories: Mapped[int] = mapped_column(Integer, nullable=False)
    protein: Mapped[float | None] = mapped_column(Numeric(6, 1), nullable=True)  # g
    fat: Mapped[float | None] = mapped_column(Numeric(6, 1), nullable=True)  # g
    carbs: Mapped[float | None] = mapped_column(Numeric(6, 1), nullable=True)  # g
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    chain: Mapped["Chain"] = relationship("Chain", back_populates="menus")
