"""提案API - 予算・カロリー内のメニューを近くの店舗と一緒に提案"""
from datetime import date
from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database import get_db
from src.models import User, Restaurant, Chain, Menu, MealLog
from src.services.geo import haversine_km
from src.services.places import fetch_nearby_restaurants

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.get("")
def recommend(
    lat: float = Query(..., description="緯度"),
    lng: float = Query(..., description="経度"),
    radius_km: float = Query(1.0, ge=0.1, le=10.0, description="検索半径(km)"),
    user_id: int | None = Query(None, description="ユーザーID（指定時は残り予算・カロリーでフィルタ）"),
    budget: int | None = Query(None, description="予算上限(円)（user_id未指定時）"),
    calories: int | None = Query(None, description="カロリー上限(kcal)（user_id未指定時）"),
    open_now: bool = Query(False, description="営業中のみ（Places API連携時）"),
    session: Session = Depends(get_db),
):
    """
    現在地付近の店舗から、予算・カロリー内のメニューを提案。

    - user_id 指定時: ユーザーの残り予算・残りカロリーで自動フィルタ
    - 未指定時: budget, calories の指定でフィルタ（未指定なら制限なし）
    """
    # 予算・カロリーの取得
    if user_id:
        user = session.get(User, user_id)
        if not user:
            return {"error": "User not found"}
        # 本日の消費を計算
        today = date.today()
        logs = (
            session.query(MealLog)
            .filter(
                MealLog.user_id == user_id,
                func.date(MealLog.eaten_at) == today,
            )
            .all()
        )
        total_cal = 0
        total_price = 0
        for log in logs:
            if log.menu_id:
                m = session.get(Menu, log.menu_id)
                total_cal += m.calories if m else 0
                total_price += m.price if m else 0
            else:
                total_cal += log.manual_calories or 0
                total_price += log.manual_price or 0
        budget_limit = max(0, user.daily_budget_limit - total_price)
        calorie_limit = max(0, user.daily_calorie_limit - total_cal)
    else:
        budget_limit = budget if budget is not None else 99999
        calorie_limit = calories if calories is not None else 99999

    # 店舗一覧を構築: 自社DB + Places API（キー設定時）
    chains = {c.chain_id: c for c in session.query(Chain).all()}
    chain_names = {c.chain_name: c.chain_id for c in chains.values()}

    # 自社DBの店舗
    nearby: list[tuple[Any, str, float]] = []  # (restaurant_or_place, chain_name, dist_km)
    for r in session.query(Restaurant).all():
        dist = haversine_km(lat, lng, float(r.latitude), float(r.longitude))
        if dist <= radius_km:
            chain = chains.get(r.chain_id)
            nearby.append((r, chain.chain_name if chain else "", dist))

    # Places API（キー設定時）: チェーン名にマッチする店舗を追加
    places_data = fetch_nearby_restaurants(
        lat, lng, radius_m=int(radius_km * 1000), open_now=open_now
    )
    if places_data:
        for p in places_data:
            dist = haversine_km(lat, lng, p["lat"], p["lng"])
            if dist > radius_km:
                continue
            name = p.get("name") or ""
            for chain_name, cid in chain_names.items():
                if chain_name in name:
                    nearby.append((p, chain_name, dist))
                    break

    # 距離順ソート
    nearby.sort(key=lambda x: x[2])

    # 各店舗のチェーンで、予算・カロリー内のメニューを取得
    results = []
    for item, chain_name, dist_km in nearby:
        chain_id = chain_names.get(chain_name)
        if not chain_id:
            continue
        restaurant = item if isinstance(item, Restaurant) else None
        place = item if isinstance(item, dict) else None
        rest_name = restaurant.name if restaurant else (place.get("name", "") or "")
        menus = (
            session.query(Menu)
            .filter(
                Menu.chain_id == chain_id,
                Menu.is_available == True,
                Menu.price <= budget_limit,
                Menu.calories <= calorie_limit,
            )
            .all()
        )
        for m in menus:
            results.append(
                {
                    "menu_id": m.menu_id,
                    "restaurant_name": rest_name,
                    "chain_name": chain_name,
                    "menu_name": m.menu_name,
                    "price": m.price,
                    "calories": m.calories,
                    "distance_km": round(dist_km, 2),
                    "distance_walk": f"徒歩約{int(dist_km * 12)}分" if dist_km < 2 else f"{dist_km:.1f}km",
                }
            )

    return {
        "budget_limit": budget_limit,
        "calorie_limit": calorie_limit,
        "count": len(results),
        "recommendations": results[:20],  # 最大20件
    }
