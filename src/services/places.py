"""Google Places API 連携サービス

環境変数 GOOGLE_PLACES_API_KEY が設定されている場合のみ実APIを呼び出し。
未設定時は None を返し、自社DBの店舗のみを使用する。
"""
import os
from typing import Any

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")


def fetch_nearby_restaurants(
    lat: float,
    lng: float,
    radius_m: int = 1000,
    open_now: bool = False,
) -> list[dict[str, Any]] | None:
    """
    現在地付近の飲食店をPlaces APIで取得。

    Returns:
        店舗リスト、または APIキー未設定時は None
    """
    if not GOOGLE_PLACES_API_KEY:
        return None

    try:
        import httpx
    except ImportError:
        return None

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "type": "restaurant",
        "key": GOOGLE_PLACES_API_KEY,
    }
    if open_now:
        params["opennow"] = "true"

    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    if data.get("status") != "OK":
        return []

    return [
        {
            "place_id": p.get("place_id"),
            "name": p.get("name"),
            "lat": p["geometry"]["location"]["lat"],
            "lng": p["geometry"]["location"]["lng"],
            "vicinity": p.get("vicinity", ""),
            "open_now": p.get("opening_hours", {}).get("open_now"),
        }
        for p in data.get("results", [])
    ]
