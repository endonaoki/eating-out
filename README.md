# Eating Out（外食特化 食事管理アプリ）

外食に特化した食事管理アプリ。希望の予算・カロリーを入力すると、地図と連携して近くのおすすめ店舗・メニューを提案する。

## コンセプト

- **外食の強みを活かす**: チェーン店は価格・カロリーが明確 → 入力の手間が不要
- **予算内で提案**: 物価高騰時代に、希望金額内のメニューを自動でリコメンド
- **地図連携**: 現在地から徒歩圏内の店舗を表示

## ドキュメント

- [要件定義書](docs/REQUIREMENTS.md)
- [GitHubセットアップ手順](docs/GITHUB_SETUP.md)

## プロジェクト構成

```
eating-out/
├── config.py       # 設定
├── main.py        # FastAPI エントリーポイント
├── docs/          # 設計・要件定義
├── scripts/       # シードスクリプト
├── src/
│   ├── api/       # API ルート
│   ├── database/  # DB接続
│   └── models/    # SQLAlchemy モデル
└── data/          # SQLite DB（gitignore）
```

## セットアップ

```bash
cd eating-out
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/seed_chains.py       # チェーン・メニュー投入
python scripts/seed_restaurants.py   # 店舗投入（八王子・新宿・渋谷等）
python scripts/migrate_nutrition.py # 栄養素カラム追加
python scripts/update_menu_nutrition.py  # メニューに栄養素推定値を追加
python main.py
```

API: http://localhost:8000  
Swagger: http://localhost:8000/docs

## 使い方

1. `python main.py` で起動
2. ブラウザで http://localhost:8000 を開く
3. 目標カロリー・予算・性別・生年を設定
4. **現在地から検索** または **地図で場所を指定**（勤務先・最寄駅など）でメニューを検索
5. 食べたメニューを記録
6. **健康バランス**で日/週/月/年の栄養摂取を確認

## 主なAPI

| エンドポイント | 説明 |
|----------------|------|
| `GET /chains` | チェーン一覧 |
| `GET /chains/{id}/menus` | メニュー一覧 |
| `POST /users` | ユーザー作成 |
| `GET /meal-logs/users/{id}/today` | 本日の残り予算・カロリー |
| `GET /recommend?lat=&lng=&budget=&calories=` | 近くの店舗×メニュー提案 |

## 環境変数（.env）

- `GOOGLE_PLACES_API_KEY` … 設定時、Places APIで店舗検索を拡張（営業中フィルタ対応）
