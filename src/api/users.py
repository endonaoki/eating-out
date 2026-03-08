"""ユーザーAPI"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import User
from src.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
def create_user(data: UserCreate, session: Session = Depends(get_db)):
    """ユーザー作成"""
    user = User(
        daily_calorie_limit=data.daily_calorie_limit,
        daily_budget_limit=data.daily_budget_limit,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_db)):
    """ユーザー取得"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, session: Session = Depends(get_db)):
    """ユーザー設定更新"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if data.daily_calorie_limit is not None:
        user.daily_calorie_limit = data.daily_calorie_limit
    if data.daily_budget_limit is not None:
        user.daily_budget_limit = data.daily_budget_limit
    session.commit()
    session.refresh(user)
    return user
