"""チェーン・メニューAPI"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Chain, Menu

router = APIRouter(prefix="/chains", tags=["chains"])


@router.get("")
def list_chains(session: Session = Depends(get_db)):
    """チェーン一覧"""
    chains = session.query(Chain).all()
    return [
        {
            "chain_id": c.chain_id,
            "chain_name": c.chain_name,
            "official_url": c.official_url,
        }
        for c in chains
    ]


@router.get("/{chain_id}/menus")
def list_menus(chain_id: int, session: Session = Depends(get_db)):
    """チェーン別メニュー一覧"""
    menus = (
        session.query(Menu)
        .filter(Menu.chain_id == chain_id, Menu.is_available == True)
        .all()
    )
    return [
        {
            "menu_id": m.menu_id,
            "menu_name": m.menu_name,
            "price": m.price,
            "calories": m.calories,
        }
        for m in menus
    ]
