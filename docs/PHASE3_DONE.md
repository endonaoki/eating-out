# Phase 3 完了報告

## 実装内容

### 1. User API

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/users` | ユーザー作成（目標カロリー・予算を設定） |
| GET | `/users/{user_id}` | ユーザー取得 |
| PATCH | `/users/{user_id}` | ユーザー設定更新 |

### 2. Meal Logs API

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/meal-logs/users/{user_id}` | 食事記録を追加 |
| GET | `/meal-logs/users/{user_id}/today` | 本日のサマリー（残り予算・カロリー） |

### 3. 提案API（Recommend）

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/recommend` | 現在地付近の店舗×メニューを提案 |

**クエリパラメータ:**

| パラメータ | 必須 | 説明 |
|------------|------|------|
| lat | ✓ | 緯度 |
| lng | ✓ | 経度 |
| radius_km | | 検索半径(km)、デフォルト1.0 |
| user_id | | 指定時は残り予算・カロリーで自動フィルタ |
| budget | | user_id未指定時の予算上限(円) |
| calories | | user_id未指定時のカロリー上限(kcal) |

**例:**
```
GET /recommend?lat=35.6896&lng=139.6917&radius_km=2&budget=1000&calories=800
```

### 4. 店舗シードデータ

東京・神奈川周辺に13店舗を登録（新宿、渋谷、池袋、横浜など）。

---

## 次のフェーズ（Phase 4）

- フロントエンド（Web / モバイル）の検討
- Google Places API 連携（実店舗の動的取得）
- 営業中フィルタ
