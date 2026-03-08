"""Chain モデル"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Chain(Base, TimestampMixin):
    __tablename__ = "chains"

    chain_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chain_name: Mapped[str] = mapped_column(String(100), nullable=False)
    official_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    restaurants: Mapped[list["Restaurant"]] = relationship("Restaurant", back_populates="chain")
    menus: Mapped[list["Menu"]] = relationship("Menu", back_populates="chain")
