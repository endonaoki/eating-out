#!/usr/bin/env python3
"""
店舗シードデータ投入スクリプト

チェーン店のサンプル店舗（東京周辺）を登録。
※ seed_chains.py を先に実行すること。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import init_db, get_session
from src.models import Chain, Restaurant

# チェーン名 -> 店舗リスト（名前, 緯度, 経度）
# 東京・神奈川・八王子周辺の主要駅付近
RESTAURANTS = [
    # 八王子（元横山町・八王子駅周辺）
    ("大戸屋", "大戸屋 八王子店", 35.6649, 139.3382),
    ("すき家", "すき家 八王子駅前店", 35.6556, 139.3389),
    ("サイゼリヤ", "サイゼリヤ 八王子店", 35.6595, 139.3456),
    ("マクドナルド", "マクドナルド 八王子駅前店", 35.6556, 139.3389),
    ("松屋", "松屋 八王子店", 35.6595, 139.3456),
    # 新宿・渋谷・池袋
    ("大戸屋", "大戸屋 新宿店", 35.6896, 139.6917),
    ("大戸屋", "大戸屋 渋谷店", 35.6595, 139.7004),
    ("大戸屋", "大戸屋 池袋店", 35.7295, 139.7109),
    ("すき家", "すき家 新宿東口店", 35.6896, 139.7047),
    ("すき家", "すき家 渋谷道玄坂店", 35.6595, 139.6987),
    ("すき家", "すき家 池袋西口店", 35.7295, 139.7109),
    ("サイゼリヤ", "サイゼリヤ 新宿店", 35.6896, 139.6917),
    ("サイゼリヤ", "サイゼリヤ 渋谷店", 35.6595, 139.7004),
    ("サイゼリヤ", "サイゼリヤ 横浜店", 35.4658, 139.6228),
    ("マクドナルド", "マクドナルド 新宿駅前店", 35.6896, 139.6917),
    ("マクドナルド", "マクドナルド 渋谷スクランブル店", 35.6595, 139.7004),
    ("松屋", "松屋 新宿店", 35.6896, 139.6917),
    ("松屋", "松屋 渋谷店", 35.6595, 139.7004),
]


def main():
    init_db()
    session = get_session()
    try:
        chains = {c.chain_name: c.chain_id for c in session.query(Chain).all()}
        if not chains:
            print("エラー: 先に python scripts/seed_chains.py を実行してください")
            sys.exit(1)

        count = 0
        for chain_name, name, lat, lng in RESTAURANTS:
            if chain_name not in chains:
                continue
            existing = session.query(Restaurant).filter(
                Restaurant.name == name,
                Restaurant.chain_id == chains[chain_name],
            ).first()
            if existing:
                continue
            r = Restaurant(
                chain_id=chains[chain_name],
                name=name,
                latitude=lat,
                longitude=lng,
            )
            session.add(r)
            count += 1

        session.commit()
        print(f"✓ {count} 店舗を登録しました")
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
