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


def _get_nutrition_from_menu(session: Session, menu) -> dict:
    """Menuから栄養素を取得（推定含む）"""
    p = float(menu.protein or 0)
    f = float(menu.fat or 0)
    c = float(menu.carbs or 0)
    return {
        "protein": p,
        "fat": f,
        "carbs": c,
        "iron": p * 0.15 + c * 0.02,
        "calcium": p * 5 + f * 2,
        "vitamin_c": c * 0.5,
    }


@router.get("")
def recommend(
    lat: float = Query(..., description="緯度"),
    lng: float = Query(..., description="経度"),
    radius_km: float = Query(5.0, ge=1.0, le=15.0, description="検索半径(km)"),
    user_id: int | None = Query(None, description="ユーザーID（指定時は残り予算・カロリーでフィルタ）"),
    budget: int | None = Query(None, description="予算上限(円)（user_id未指定時）"),
    calories: int | None = Query(None, description="カロリー上限(kcal)（user_id未指定時）"),
    open_now: bool = Query(False, description="営業中のみ（Places API連携時）"),
    by_deficit: bool = Query(False, description="足りない栄養を補うメニューを優先"),
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

    # 足りない栄養の計算（by_deficit時）
    deficit = {}
    if by_deficit and user_id:
        today = date.today()
        logs = (
            session.query(MealLog)
            .filter(
                MealLog.user_id == user_id,
                func.date(MealLog.eaten_at) == today,
            )
            .all()
        )
        total_p, total_f, total_c = 0, 0, 0
        for log in logs:
            if log.menu_id:
                m = session.get(Menu, log.menu_id)
                if m:
                    total_p += float(m.protein or 0)
                    total_f += float(m.fat or 0)
                    total_c += float(m.carbs or 0)
            else:
                total_p += float(log.manual_protein or 0)
                total_f += float(log.manual_fat or 0)
                total_c += float(log.manual_carbs or 0)
        u = session.get(User, user_id)
        if u:
            age = (today.year - u.birth_year) if u.birth_year else 35
            base_cal = 2000 if (u.gender or "").lower() != "female" else 1800
            if age >= 30:
                base_cal -= (age - 30) // 10 * 50
            rec_p = base_cal * 0.2 / 4
            rec_f = base_cal * 0.25 / 9
            rec_c = base_cal * 0.55 / 4
            deficit = {
                "protein": max(0, rec_p - total_p),
                "fat": max(0, rec_f - total_f),
                "carbs": max(0, rec_c - total_c),
            }

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
            r = {
                "menu_id": m.menu_id,
                "restaurant_name": rest_name,
                "chain_name": chain_name,
                "menu_name": m.menu_name,
                "price": m.price,
                "calories": m.calories,
                "distance_km": round(dist_km, 2),
                "distance_walk": f"徒歩約{int(dist_km * 12)}分" if dist_km < 2 else f"{dist_km:.1f}km",
            }
            if deficit:
                n = _get_nutrition_from_menu(session, m)
                score = 0
                if deficit.get("protein", 0) > 0:
                    score += n["protein"] * 2
                if deficit.get("fat", 0) > 0:
                    score += n["fat"]
                if deficit.get("carbs", 0) > 0:
                    score += n["carbs"]
                r["_deficit_score"] = score
            results.append(r)

    if deficit:
        results.sort(key=lambda x: x.get("_deficit_score", 0), reverse=True)
        for r in results:
            r.pop("_deficit_score", None)

    return {
        "budget_limit": budget_limit,
        "calorie_limit": calorie_limit,
        "deficit": deficit if deficit else None,
        "count": len(results),
        "recommendations": results[:20],
    }
