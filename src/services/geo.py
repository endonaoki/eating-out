"""地理計算ユーティリティ"""
from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """2点間の距離（km）をハーバーサイン公式で計算"""
    R = 6371  # 地球の半径 km
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
