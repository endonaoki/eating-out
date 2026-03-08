"""Restaurant モデル"""
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Restaurant(Base, TimestampMixin):
    __tablename__ = "restaurants"

    restaurant_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chain_id: Mapped[int] = mapped_column(Integer, ForeignKey("chains.chain_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    place_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)

    chain: Mapped["Chain"] = relationship("Chain", back_populates="restaurants")
