# Development Log

## 1. プロジェクト概要

League of Legends の戦績を取得・分析する Web アプリを作成する。

学校で学習している以下の技術を、実際のアプリ開発で活用することも目的としている。

- Python
- HTML
- CSS
- JavaScript
- DB / SQL
- Linux
- Git / GitHub

現在は Riot Games API を利用して、Riot ID からプレイヤーを検索し、直近の試合情報を取得する機能を開発している。


## 2. 使用技術

### Python

用途:

- Flask を使ったバックエンド処理
- Riot API へのHTTPリクエスト
- JSONデータの処理
- Riot APIから取得した試合データの分析

使った理由:

学校でPythonを学習しているため。

授業で学んだ変数、辞書、リスト、for文、if文などを、実際のWebアプリでどのように使うのか理解するため。


### Flask

用途:

- Webサーバーの起動
- URLごとの処理（ルーティング）
- HTMLの表示
- JavaScriptから送られたデータの受信
- JSONレスポンスの返却

使った理由:

PythonでWebアプリを作るため。

比較的シンプルなフレームワークなので、Webアプリの仕組みを理解しながら開発しやすい。


### HTML

用途:

- Webページの基本構造
- Riot IDの入力フォーム
- ゲーム名・タグラインの入力欄
- 検索ボタン


### CSS

用途:

- Webページのデザイン
- 背景色や文字色などの設定

FlaskではCSSファイルを `static/css/` に配置し、HTMLから `url_for()` を使って読み込んでいる。


### JavaScript

用途:

- HTMLフォームに入力された値を取得
- フォーム送信時の処理
- `fetch()` を使ったFlaskとのHTTP通信
- Flaskから返されたJSONデータの受け取り

使った理由:

ページ全体を再読み込みせずに、ブラウザとFlaskの間でデータをやり取りするため。


### Git / GitHub

用途:

- ソースコードのバージョン管理
- 開発履歴の保存
- 2台のPC間でコードを同期
- ポートフォリオとして開発過程を残す

基本的な流れ:

```text
コードを変更
↓
git add
↓
git commit
↓
git push
↓
GitHubへ反映
```

別のPCで作業するときは、作業開始前に `git pull` を実行して最新状態を取得する。


### Riot Games API

用途:

- Riot IDからアカウント情報を取得
- PUUIDを取得
- PUUIDから試合ID一覧を取得
- 試合IDから試合詳細を取得

現在使用しているAPI:

#### ACCOUNT-V1

Riot IDから以下の情報を取得する。

- gameName
- tagLine
- puuid

#### MATCH-V5

PUUIDから直近の試合ID一覧を取得する。

さらに試合IDを使って、1試合の詳細データを取得する。


### requests

用途:

PythonからRiot APIへHTTPリクエストを送るために使用。

JavaScriptでは `fetch()` を使い、Pythonでは `requests.get()` を利用している。


### python-dotenv

用途:

Riot API Keyを `.env` からPythonへ読み込むために使用。

APIキーをソースコードに直接書かないために利用している。


## 3. 現在までに実装した流れ

現在は以下の流れまで実装できている。

```text
ユーザーがRiot IDを入力
↓
HTMLフォーム
↓
JavaScriptでgameNameとtagLineを取得
↓
fetch()でFlaskの /search にPOST
↓
Flaskがrequest.get_json()でJSONを受信
↓
gameNameとtagLineを取得
↓
Riot ACCOUNT-V1へリクエスト
↓
PUUIDを取得
↓
PUUIDを使ってMATCH-V5へリクエスト
↓
直近20試合の試合ID一覧を取得
↓
リストの先頭から最新試合IDを取得
↓
最新試合の詳細データを取得
↓
participantsから10人分のデータを取得
↓
PUUIDを比較して検索した本人を特定
↓
本人が使用したChampionを取得
```

現在、最新試合で使用したChampion名まで取得できている。


## 4. 学んだこと

### Flaskの役割

Flaskは、ブラウザとPythonをつなぐバックエンドとして使用している。

例えば、

```python
@app.route("/")
```

ではトップページを表示し、

```python
@app.route("/search", methods=["POST"])
```

ではJavaScriptから送られたデータを受け取っている。


### fetch()

JavaScriptからFlaskへHTTP通信するために使用した。

```javascript
fetch("/search", {
    method: "POST"
})
```

を使うことで、JavaScriptからFlaskへデータを送信できる。


### GETとPOST

GET:

主にデータを取得するときに使用する。

今回、PythonからRiot APIへアクセスするときに `requests.get()` を使用している。

POST:

データをサーバーへ送るときに使用する。

今回、JavaScriptからFlaskへRiot IDを送るときに使用している。


### JSON

JavaScript・Flask・Riot APIの間でデータをやり取りするためにJSONを使用している。

JavaScriptでは、

```javascript
JSON.stringify({
    gameName: gameName,
    tagline: tagline
})
```

としてFlaskへ送信している。

Flaskでは、

```python
data = request.get_json()
```

として受け取っている。


### Pythonの辞書

Riot APIから返されたJSONを、

```python
riot_data = response.json()
```

としてPythonの辞書として扱った。

例えばPUUIDは、

```python
puuid = riot_data["puuid"]
```

として取得した。


### Pythonのリスト

MATCH-V5から取得した試合ID一覧はリストとして返される。

```python
match_ids = match_response.json()
```

最新試合のIDは、

```python
latest_match_id = match_ids[0]
```

として取得した。


### for文とif文

1試合には10人分の `participants` データが存在する。

その中から検索した本人を探すために、

```python
for participant in participants:
    if participant["puuid"] == puuid:
```

として、1人ずつPUUIDを比較した。

これによって、検索した本人の試合データだけを取得できた。


### PUUID

PUUIDはRiotのプレイヤーを一意に識別するID。

今回のアプリでは、

```text
Riot ID
↓
PUUID
↓
試合履歴
```

という流れで使用している。


### HTTPステータスコード

今回確認した主なステータスコード:

#### 200 OK

リクエスト成功。

#### 401 Unauthorized

Riot API Keyが認識されなかったときに発生した。

#### 404 Not Found

存在しないファイルなどへアクセスした場合に発生する。

開発中は `favicon.ico` が存在しなかったため404が表示された。


### HTTP通信は1つではない

今回のアプリでは、

```text
ブラウザ
↓
Flask
```

と、

```text
Flask
↓
Riot API
```

は別々のHTTP通信である。

そのため、Riot APIが401を返していても、Flaskが正常にレスポンスを返せば、

```text
POST /search 200
```

と表示されることがある。

どの通信のステータスコードなのかを確認する必要があると学んだ。


### .env

Riot API Keyは `.env` に保存している。

```env
RIOT_API_KEY=...
```

Pythonでは、

```python
load_dotenv()
api_key = os.getenv("RIOT_API_KEY")
```

として読み込む。

`.gitignore` に、

```text
.env
```

を追加しているため、APIキーはGitHubにpushされない。

APIキーなどの秘密情報をソースコードへ直接書かないことが重要だと学んだ。


### 仮想環境 .venv

Pythonのライブラリをプロジェクトごとに分離するため `.venv` を使用している。

必要なライブラリは、

```powershell
pip freeze > requirements.txt
```

で保存する。

別のPCでは、

```powershell
pip install -r requirements.txt
```

を実行することで、必要なライブラリを再現できる。


### GitとGitHubの違い

Git:

自分のPC上でファイルの変更履歴を管理する。

GitHub:

Gitで管理しているリポジトリをインターネット上に保存・共有する。

2台のPCで開発しているため、

```text
PC1
↓
git push
↓
GitHub
↓
git pull
↓
PC2
```

という形でコードを同期している。


## 5. 発生したエラーと解決

### Gitコマンドが認識されない

問題:

PowerShellで `git` が認識されなかった。

原因:

Gitがインストールされていなかった、またはPATHが反映されていなかった。

解決:

GitをインストールしてPowerShellを再起動した。


### PowerShellで仮想環境を有効化できない

エラー:

```text
このシステムではスクリプトの実行が無効になっています
```

原因:

PowerShellのExecution Policyによって `Activate.ps1` の実行が禁止されていた。

解決:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

を実行して、現在のPowerShellだけ一時的に許可した。


### GitでAuthor identity unknown

原因:

2台目のPCでGitのユーザー名とメールアドレスが設定されていなかった。

解決:

```powershell
git config --global user.name "ユーザー名"
git config --global user.email "メールアドレス"
```

を設定した。


### Riot APIで401 Unknown apikey

エラー:

```json
{
    "status": {
        "message": "Unknown apikey",
        "status_code": 401
    }
}
```

原因:

使用していたDevelopment API KeyがRiot側で認識されていなかった。

解決:

Riot Developer PortalでAPI Keyを再発行し、`.env` を更新した。

その後Flaskを再起動し、200が返ることを確認した。


### requests.exceptions.MissingSchema

間違っていたコード:

```python
requests.get(api_key, headers=headers)
```

原因:

`requests.get()` の第1引数にはURLを渡す必要があるが、誤ってAPI Keyを渡していた。

正しい形:

```python
requests.get(match_url, headers=headers)
```

このエラーから、

```python
requests.get(URL, headers=HTTPヘッダー)
```

という基本的な使い方を理解した。


## 6. 次にやること

現在は検索した本人のChampion名まで取得できている。

次は `participant` から以下のデータを取得する。

- Champion
- Kills
- Deaths
- Assists
- Win / Lose

その後、

```text
Kills / Deaths / Assists取得
↓
KDAを計算
↓
FlaskからJavaScriptへJSONで返す
↓
JavaScriptでデータを受け取る
↓
HTML上に戦績を表示
```

まで実装する。

その後は以下の機能を追加する予定。

- 直近複数試合の取得
- 勝率の計算
- 平均KDA
- CS
- Vision Score
- Champion別成績
- MySQLへの試合データ保存
- SQLを使った戦績分析
- WebページのUI改善
- Linuxサーバーへのデプロイ