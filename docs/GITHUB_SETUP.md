# GitHub セットアップ手順

## 1. GitHubでリポジトリを作成

1. [GitHub](https://github.com) にログイン
2. 右上の **+** → **New repository**
3. 以下を設定:
   - **Repository name**: `eating-out`
   - **Description**: 外食特化 食事管理アプリ
   - **Public** を選択
   - **Add a README file** は **チェックしない**（既にローカルにあるため）
4. **Create repository** をクリック

## 2. ローカルをGitHubにプッシュ

作成後、GitHubに表示されるコマンドを実行します。ユーザー名を `YOUR_USERNAME` に置き換えてください。

```bash
cd /Users/endounaoki/Desktop/keiba/oracle-x/eating-out

# リモートを追加
git remote add origin https://github.com/YOUR_USERNAME/eating-out.git

# 初回プッシュ
git add .
git commit -m "Initial commit: 要件定義・プロジェクト構成"
git branch -M main
git push -u origin main
```

## 3. GitHub CLI を使う場合（オプション）

`gh` がインストールされていれば、以下で一括作成できます。

```bash
brew install gh
gh auth login
cd /Users/endounaoki/Desktop/keiba/oracle-x/eating-out
gh repo create eating-out --public --source=. --push
```
