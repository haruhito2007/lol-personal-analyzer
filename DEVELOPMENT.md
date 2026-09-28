# Development Log

## 1. プロジェクト概要
LoLの戦績を取得・分析するWebアプリを作成する。

## 2. 使用技術

### Python
用途:
- Flaskによるバックエンド処理
- Riot APIへのリクエスト
- JSONデータの処理

使った理由:
- 学校で学習中
- APIやDB処理を実装しやすい

### Flask
用途:
- Webサーバー
- `/` や `/search` のルーティング
- HTMLの表示
- JavaScriptとの通信

使った理由:
- PythonでWebアプリの仕組みを理解しやすい
- 比較的シンプル

### HTML / CSS
用途:
- 検索フォーム
- 画面構成
- デザイン

### JavaScript
用途:
- フォーム入力の取得
- fetchによるFlaskとの通信
- JSONレスポンスの受け取り

### Git / GitHub
用途:
- バージョン管理
- 2台のPC間でコードを同期
- 開発履歴を残す

### Riot API
用途:
- Riot IDからPUUIDを取得
- PUUIDから試合IDを取得
- 試合詳細を取得

## 3. 現在までに実装した流れ

Riot ID入力
↓
JavaScriptで取得
↓
fetchでFlaskへPOST
↓
FlaskでJSON受信
↓
ACCOUNT-V1へアクセス
↓
PUUID取得
↓
MATCH-V5で試合ID取得
↓
最新試合を取得
↓
participantsから本人を特定
↓
使用チャンピオン取得

## 4. 学んだこと

### GETとPOST
GET:
- 主にデータ取得

POST:
- データをサーバーへ送る

### JSON
JavaScriptとPythonの間でデータを受け渡すために使用。

### PUUID
Riotのプレイヤーを一意に識別するID。

## 5. エラーと解決

### GitでAuthor identity unknown
原因:
Gitのuser.nameとuser.emailが未設定。

解決:
git config --global user.name ...
git config --global user.email ...

### Riot APIで401 Unknown apikey
原因:
Development API Keyが無効。

解決:
APIキーを再発行して.envを更新。

### requests.exceptions.MissingSchema
原因:
requests.get()のURL部分にAPIキーを渡していた。

修正:
requests.get(match_url, headers=headers)

## 6. 次にやること
- kills / deaths / assists / winの取得
- KDA計算
- JavaScriptへ戦績JSONを返す
- 画面表示
- DB保存