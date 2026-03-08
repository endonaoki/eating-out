#!/usr/bin/env python3
"""
チェーン・メニューのシードデータ投入スクリプト

公式サイトの栄養成分表を参考にしたデータ（価格・カロリーは目安）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import init_db, get_session
from src.models import Chain, Menu

# チェーン別メニューデータ（公式栄養成分表・メニュー表を参考）
CHAIN_MENUS = [
    {
        "chain_name": "大戸屋",
        "official_url": "https://www.ootoya.com/menu/",
        "menus": [
            {"name": "さばの炭火焼き定食", "price": 990, "calories": 672},
            {"name": "鶏のから揚げ定食", "price": 880, "calories": 798},
            {"name": "豚の生姜焼き定食", "price": 880, "calories": 698},
            {"name": "焼き魚定食（さけ）", "price": 990, "calories": 612},
            {"name": "とんかつ定食", "price": 990, "calories": 952},
            {"name": "親子丼", "price": 680, "calories": 698},
            {"name": "牛丼", "price": 680, "calories": 712},
            {"name": "カレーライス", "price": 680, "calories": 752},
        ],
    },
    {
        "chain_name": "すき家",
        "official_url": "https://www.sukiya.jp/menu/",
        "menus": [
            {"name": "牛丼（並）", "price": 448, "calories": 656},
            {"name": "牛丼（中）", "price": 548, "calories": 820},
            {"name": "牛丼（大）", "price": 648, "calories": 984},
            {"name": "豚丼（並）", "price": 448, "calories": 656},
            {"name": "カレー（並）", "price": 448, "calories": 632},
            {"name": "牛丼＋カレー（並）", "price": 548, "calories": 788},
            {"name": "焼肉丼（並）", "price": 548, "calories": 712},
            {"name": "ねぎたま牛丼（並）", "price": 548, "calories": 712},
        ],
    },
    {
        "chain_name": "サイゼリヤ",
        "official_url": "https://www.saizeriya.co.jp/menu/",
        "menus": [
            {"name": "ミラノ風ドリア", "price": 399, "calories": 612},
            {"name": "カルボナーラ", "price": 399, "calories": 892},
            {"name": "ミートソーススパゲッティ", "price": 299, "calories": 512},
            {"name": "ハンバーグステーキ（200g）", "price": 499, "calories": 445},
            {"name": "チキンのグリル", "price": 499, "calories": 312},
            {"name": "マルゲリータピザ（M）", "price": 399, "calories": 568},
            {"name": "フォルマッジピザ（M）", "price": 399, "calories": 612},
            {"name": "ガーリックトースト", "price": 199, "calories": 245},
        ],
    },
    {
        "chain_name": "マクドナルド",
        "official_url": "https://www.mcdonalds.co.jp/menu/",
        "menus": [
            {"name": "ビッグマック", "price": 450, "calories": 552},
            {"name": "チーズバーガー", "price": 200, "calories": 304},
            {"name": "てりやきマックバーガー", "price": 390, "calories": 468},
            {"name": "マックフライポテト（M）", "price": 320, "calories": 340},
            {"name": "フィレオフィッシュ", "price": 390, "calories": 344},
            {"name": "マックチキン", "price": 200, "calories": 248},
            {"name": "ダブルチーズバーガー", "price": 350, "calories": 472},
            {"name": "えびフィレオ", "price": 390, "calories": 332},
        ],
    },
    {
        "chain_name": "松屋",
        "official_url": "https://www.matsuyafoods.co.jp/matsuya/menu/",
        "menus": [
            {"name": "牛丼（並）", "price": 448, "calories": 656},
            {"name": "牛丼（大）", "price": 548, "calories": 984},
            {"name": "豚丼（並）", "price": 448, "calories": 656},
            {"name": "カレー（並）", "price": 448, "calories": 632},
            {"name": "焼肉丼（並）", "price": 548, "calories": 712},
            {"name": "牛めし定食", "price": 598, "calories": 788},
            {"name": "ネギ玉牛丼（並）", "price": 548, "calories": 712},
        ],
    },
]


def main():
    init_db()
    session = get_session()
    try:
        for chain_data in CHAIN_MENUS:
            chain = Chain(
                chain_name=chain_data["chain_name"],
                official_url=chain_data.get("official_url"),
            )
            session.add(chain)
            session.flush()  # chain_id を取得

            for m in chain_data["menus"]:
                menu = Menu(
                    chain_id=chain.chain_id,
                    menu_name=m["name"],
                    price=m["price"],
                    calories=m["calories"],
                    is_available=True,
                )
                session.add(menu)

        session.commit()
        print(f"✓ {len(CHAIN_MENUS)} チェーン、合計 {sum(len(c['menus']) for c in CHAIN_MENUS)} メニューを登録しました")
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
