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


## 7. 基本設計の開始

### 7.1 2026-11-04 UQ-001・UQ-002の設計判断

要件定義の承認後、基本設計の最初の判断として以下がユーザー承認された。

- `UQ-001`: ログインなしの個人利用を維持しながら、内部所有者IDを持つ「内部プロフィール付き単一ユーザー」を採用する。
- `UQ-002`: 正式対応をJP1、リージョナルルーティングをASIAに限定し、内部では将来拡張可能な構成を採用する。

決定内容、採用理由、関連要件、将来拡張への影響および残る未決定事項は `BASIC_DESIGN.md` に記録した。`REQUIREMENTS.md` では `UQ-001` と `UQ-002` を解決済み事項へ移動した。

この時点では、システム構成、責務分担、DBの物理構造、API呼び出し手順、画面操作などの実装方法は確定していない。詳細設計、実装、依存関係変更には進んでいない。

### 7.2 2026-11-05 システム構成・責務分担の設計判断

基本設計のシステム構成として、`BD-DEC-003`「段階的に構築するモジュラーモノリス」がユーザー承認された。

採用理由:

- 現行のFlaskアプリを残しながら、小さな単位でルーティング、Riot API通信、サービス、DBアクセス、設定を分離できる。
- 大規模な一括作り直しを避ける `BR-006` と `NFR-031` に合う。
- Riot API通信を専用クライアントへ分離することで、実APIを呼ばないモックテストを作りやすい。
- 目標・レビューの書き込み制約をサービス層へ集約し、クライアントから送られたPUUIDをそのまま信用しない設計にできる。
- 最小限のファイル分割より将来拡張しやすく、完全なクリーンアーキテクチャより学習・実装コストを抑えられる。
- 単一のFlaskアプリとして実行・デバッグでき、各構成要素の役割を段階的に学習できる。

Application Factory、Blueprint、サービス層、Riot APIクライアント、リポジトリ、設定、共通エラー処理を責務境界とする。未実装機能のモジュールを一括作成せず、機能実装に合わせて段階的に追加する。

次の事項はこの判断では確定していない。

- 他人の戦績をMySQLへ保存する範囲
- 内部所有者IDとメインPUUIDの具体的な管理方法
- Riot API通信とDBトランザクションの具体的な境界
- DB技術、キャッシュ、タイムアウト値、429時の再試行、例外形式の詳細

この時点では文書更新だけを行い、コード、DB、依存関係、詳細設計、実装には進んでいない。

### 7.3 2026-11-05 P1 STEP 1 Flaskの責務分離

P1の最初の実装として、`BD-DEC-003`に従い、既存の検索処理をApplication Factory、Blueprint、Riot API Client、Serviceへ分離した。このSTEPはリファクタリングに限定し、既存のURL、ブラウザから送るJSON、ブラウザへ返すJSONを維持した。

変更したファイル:

- `app.py`: `create_app()`を呼び出して起動する薄い入口へ変更した。
- `summoners_note/__init__.py`: Application Factoryを追加し、設定読込、Client・Service生成、Blueprint登録を行うようにした。
- `summoners_note/config.py`: Riot APIキーとリージョナルルートの設定を集約した。
- `summoners_note/routes/search.py`: `/` と `/search` のHTTP入出力をBlueprintへ移した。
- `summoners_note/clients/riot_api.py`: `requests`によるACCOUNT-V1・MATCH-V5通信を専用Clientへ移した。
- `summoners_note/services/player_search.py`: Riot ID検索、PUUID取得、試合ID取得、試合詳細取得、対象participant検索の処理順序をServiceへ移した。
- `summoners_note/routes/__init__.py`、`summoners_note/clients/__init__.py`、`summoners_note/services/__init__.py`: 各ディレクトリをPythonパッケージとして整理した。
- `tests/__init__.py`、`tests/test_app.py`: 標準ライブラリの`unittest`と`unittest.mock`、Flaskテストクライアントによるテストを追加した。

各モジュールの役割:

- Application FactoryはFlaskアプリを生成し、テスト用設定とモックClientを差し替えられるようにする。
- BlueprintはHTTPリクエストを受け取り、Serviceを呼び出し、HTTPレスポンスを返す。
- ServiceはRiot IDから試合詳細まで取得する処理順序を担当し、Flaskの`request`へ依存しない。
- Riot API ClientはURL構築、認証ヘッダー、外部HTTP通信を担当する。
- Configは秘密情報とASIAルートをコードの各所へ分散させない。

分離した理由:

- Routeから外部通信と処理全体の制御を外し、各部分の責務を確認しやすくするため。
- 実際のRiot APIを呼ばず、Clientをモックへ差し替えてServiceとRouteをテストするため。
- P1の後続STEPでJP1所属確認、対象queue指定、エラー分類を小さな単位で追加するため。
- 既存の`templates/`と`static/`を維持し、大規模な作り直しを避けるため。

使用したPython・Flaskの仕組み:

- `create_app(test_config=None, *, riot_api_client=None)`のキーワード専用引数を使い、本番用Clientとテスト用モックを切り替えられるようにした。
- `pathlib.Path`でリポジトリ直下の`templates/`と`static/`の位置をApplication Factoryへ明示した。
- Flaskの`Blueprint`で既存の`/`と`/search`を登録した。
- `app.extensions`へServiceを登録し、Blueprintから現在のFlaskアプリに対応するServiceを取得した。
- `Mock(spec=RiotApiClient)`を使い、存在するClientメソッドだけを想定したモックを作成した。

処理の流れ:

```text
ブラウザ
↓
Blueprint（HTTP入力）
↓
PlayerSearchService（処理順序）
↓
RiotApiClient（外部HTTP通信）
↓
PlayerSearchService（対象participant検索）
↓
Blueprint（既存JSONレスポンス）
```

実施したテスト:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

5件すべて成功した。

- Application Factoryでアプリを生成し、テスト用設定を反映できる。
- トップページ、既存CSS、既存JavaScriptを取得できる。
- `/search`が既存のPOST JSONを受け取り、既存形式のJSONを返す。
- モックClientのACCOUNT-V1、試合ID、試合詳細の各処理が順番に呼ばれる。
- Riot API ClientがConfigから受け取ったASIAルートとAPIキーをURL・認証ヘッダーへ使用する。
- participantsから検索対象PUUIDと一致するプレイヤーを取得できる。
- テスト中に`requests.Session.get()`が呼ばれず、外部Riot API通信が発生しない。
- テスト用APIキーがレスポンスへ含まれない。

テスト実装中の問題と解決:

- 静的ファイルのテストでレスポンスを閉じていなかったため`ResourceWarning`が発生した。CSSとJavaScriptのレスポンスを確認後に`close()`するよう修正した。
- モックの全呼び出し履歴には`response.json()`も含まれるため、`assert_has_calls()`ではHTTP呼び出しだけを連続比較できなかった。`session.get.call_args_list`を比較し、直接のHTTP呼び出しだけを検証するよう修正した。

発見した問題と未対応事項:

- 入力不足・形式不正をまだ検証していない。
- Riot APIのHTTPステータス、タイムアウト、JSON不正をまだ処理していない。
- 試合IDが0件の場合は、現在もリストの先頭参照でエラーになる。
- Riot IDのパス要素を安全に扱う処理は未実装である。
- JP1所属確認は未実装であり、ASIAルートで検索できたことをJP1所属の証明には使用しない。
- MATCH-V5へqueue、start、countをまだ指定していない。
- queueId確認、K/D/A、KDA、画面上の戦績カードは未実装である。
- `app.py`の直接起動では既存どおりデバッグモードを有効にしている。本番相当環境で無効化する設定は後続で扱う。
- 実Riot APIを使った動作確認は行っていない。

次はP1 STEP 2として、ACCOUNT-V1のactive region APIの公式仕様を確認し、推測を使わずにJP1所属判定を設計・実装できるか判断する。

### 7.4 2026-11-05 P1 STEP 2 JP1所属確認

Riot IDはASIAルートで検索できるが、ASIAでPUUIDを取得できたことやタグラインだけではJP1所属を証明できない。そのため、試合取得前にACCOUNT-V1のactive region APIを呼び出し、検索対象がJP1所属と確認できた場合だけ処理を続けるようにした。

#### 公式仕様と実測結果の区別

公式リファレンスでは、次の内容を確認した。

- エンドポイントは`GET /riot/account/v1/region/by-game/{game}/by-puuid/{puuid}`である。
- LoLの`game`指定値は`lol`である。
- `AccountRegionDTO`は`game`、`puuid`、`region`を持つ。
- `region`はプレイヤーのactive regionを表すが、具体的な戻り値の一覧は掲載されていない。

ユーザー承認を受けた実API検証では、既知のJP1アカウント1件について、`game="lol"`、`region="jp1"`を実測した。この値は実測根拠であり、すべてのリージョンについて公式に列挙された仕様ではない。

今回のJP1確認条件は次のすべてを満たす場合に限定した。

1. active region APIがHTTP 200相当の正常なJSONを返す。
2. `game`が`lol`と完全一致する。
3. レスポンスの`puuid`がRiot ID検索で取得したPUUIDと完全一致する。
4. `region`が実測値`jp1`と完全一致する。

`jp1`以外の値は、非JP1の具体値をまだ実測・確認できていないため、海外所属とは断定せず「所属不明」として試合取得を停止する。404、API障害、レスポンス不正も同様に、海外所属を意味するものとして扱わない。

#### 変更内容と役割

- `summoners_note/clients/riot_api.py`
  - active region取得メソッドを追加した。
  - 接続3.05秒、応答10秒のタイムアウトを共通通信処理へ設定した。
  - 401、403、404、429、5xx、タイムアウト、通信障害、JSON不正を型付き例外へ変換した。
  - 429の`Retry-After`は数字だけを安全に引き継ぎ、自動再試行は行わない。
  - account、active region、試合ID一覧、試合詳細の最低限のJSON構造を検証するようにした。
- `summoners_note/services/player_search.py`
  - PUUID取得後、試合ID取得前にactive regionを確認する順序へ変更した。
  - Riot ID検索の404、所属確認の404、未知のregion、game・PUUID不一致を区別した。
  - JP1を確認できない場合、MATCH-V5を呼び出さない。
- `summoners_note/errors.py`
  - アプリケーション内の型付き例外と、安全なJSONへ変換する共通エラーハンドラを追加した。
  - APIキー、PUUID、外部APIのレスポンス本文をブラウザへ返さない。
- `summoners_note/config.py`、`summoners_note/__init__.py`
  - タイムアウト設定をConfigへ集約し、Application FactoryでClientとエラーハンドラを設定した。
- `tests/test_app.py`
  - active region確認と異常系のモックテストを追加した。

正常時の処理は次のとおりである。

```text
Riot ID
↓
ACCOUNT-V1でPUUID取得
↓
active region取得
↓
game・PUUID・region=jp1を確認
↓
既存の試合ID・試合詳細取得へ進む
```

異常時は、ClientまたはServiceが型付き例外を発生させ、共通エラーハンドラが安全なエラーコードと案内文へ変換する。active region確認後の条件を満たさない場合は、試合取得を実行しない。

#### テスト

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

15件すべて成功した。テスト中に実Riot API通信は行っていない。

- `jp1`確認時だけ既存検索処理が続行される。
- 未確認のregion値で試合取得を停止する。
- Riot ID検索404と所属確認404を区別する。
- `game`または`puuid`が一致しない場合に停止する。
- 401、403、404、429、500、503を分類する。
- 429の`Retry-After`を返し、自動再試行しない。
- タイムアウト時に再試行せず停止する。
- JSON不正と必須フィールド欠損を拒否する。
- エラーレスポンスへAPIキー、PUUID、未確認region値を含めない。
- 既存のトップページ、CSS、JavaScript、`/search`の正常レスポンスを維持する。

#### 残る課題

- 非JP1アカウントのactive region実測値と、公式なregion値一覧は未確認である。
- 大文字・小文字が常に固定されるかは公式資料で確認できていないため、実測値`jp1`との完全一致だけを採用している。
- Riot IDの入力検証とURLパス要素の安全な組み立ては未実装である。
- 試合IDが0件の場合、試合詳細のqueue確認、participant欠損、K/D/A・KDAはSTEP 3で扱う。
- 画面上のエラー案内と戦績カードはSTEP 4で扱う。

次はP1 STEP 3として、MATCH-V5へ`queue=420`、`start=0`、`count=1`を指定し、Solo/Duo最新1試合の取得、対象participant抽出、K/D/A・KDA計算と関連する異常系を実装する。

### 7.5 2026-11-05 P1 STEP 3 Solo/Duo最新1試合の戦績取得

JP1所属確認済みのプレイヤーについて、Solo/Duoランクの最新1試合だけを取得し、チャンピオン、勝敗、Kill、Death、Assist、KDAをJSONで返すバックエンド処理を追加した。HTML、CSS、JavaScriptの画面表示は変更していない。

#### MATCH-V5の取得条件

試合ID一覧には次のクエリパラメータを指定する。

- `queue=420`: Solo/Duoランクだけを対象にする。
- `start=0`: 新しい順の先頭から取得する。
- `count=1`: 最新1試合だけ取得する。

試合詳細取得後も`info.queueId`が整数の`420`であることをServiceで再確認する。APIが想定外の試合を返した場合は、別モードの試合を代わりに表示せず`unexpected_queue`として停止する。

#### 入力検証とURL構築

- `gameName`と`tagline`が文字列であることを確認する。
- 前後の空白を除去した後、空文字にならないことを確認する。
- 改行やタブなどの制御文字を拒否する。
- 不正入力ではRiot APIを呼び出さず`invalid_riot_id`を返す。
- Riot ID、PUUID、Match IDは`urllib.parse.quote(..., safe="")`でパス要素として安全にエンコードする。
- MATCH-V5の`queue`、`start`、`count`は`requests`の`params`で指定し、文字列連結でクエリを作らない。

#### participantの抽出

試合詳細の`info.participants`を順に確認し、Riot ID検索で得たPUUIDと一致する辞書を本人のparticipantとして使用する。

```python
participant = next(
    (
        candidate
        for candidate in participants
        if isinstance(candidate, dict)
        and candidate.get("puuid") == puuid
    ),
    None,
)
```

対象participantがない場合は`participant_not_found`とする。`championName`、`win`、`kills`、`deaths`、`assists`は存在と型を確認し、Kill、Death、Assistは0以上の整数だけを受け入れる。Pythonでは`bool`が`int`の派生型であるため、数値検証では`True`や`False`を整数として受け入れないよう明示的に除外する。

#### KDA計算

Deathが1以上の場合は次の式を使用する。

```python
kda = (kills + assists) / deaths
```

Deathが0の場合はゼロ除算を避け、P1の暫定方針として次のように計算する。

```python
kda = float(kills + assists)
zero_deaths = True
```

レスポンスへ`zeroDeaths`を含めるため、画面側は通常のKDAと0デス時の暫定値を区別できる。Serviceでは計算結果を丸めない。表示上の小数点桁数はSTEP 4のJavaScriptで調整する。計算時点で丸めると、将来の集計や別表示で精度を再利用できなくなるためである。

#### JSONレスポンス

既存の`gameName`と`tagline`を維持し、`latestMatch`を追加した。

```json
{
  "gameName": "ExamplePlayer",
  "tagline": "TEST",
  "latestMatch": {
    "championName": "Ahri",
    "win": true,
    "kills": 10,
    "deaths": 2,
    "assists": 8,
    "kda": 9.0,
    "zeroDeaths": false
  }
}
```

Solo/Duoの試合IDが0件の場合は障害ではないため、HTTP 200で`latestMatch: null`を返す。別queueの試合で補完しない。

#### データの流れと責務

```text
Blueprint
  HTTP JSONを受信し、Serviceの結果をJSONレスポンスへ変換
↓
PlayerSearchService
  入力検証 → PUUID → JP1確認 → queue条件指定
  → queueId再確認 → participant抽出 → KDA計算
↓
RiotApiClient
  パスのエンコード、クエリパラメータ、認証、タイムアウト、HTTP・JSON処理
```

Clientは「Riot APIへどう通信するか」を担当し、Serviceは「どの順番で取得し、どのデータを採用・計算するか」を担当する。

#### 変更したファイル

- `summoners_note/routes/search.py`: JSON入力を安全に読み、Serviceの結果をJSON化する。
- `summoners_note/clients/riot_api.py`: パスエンコードとMATCH-V5クエリパラメータを追加する。
- `summoners_note/services/player_search.py`: 入力検証、最新1試合、queue確認、participant抽出、KDA計算を追加する。
- `summoners_note/errors.py`: 入力不正、queue不一致、participant不在の安全なエラーを追加する。
- `tests/test_app.py`: STEP 3の正常系・異常系テストを追加する。
- `DEVELOPMENT.md`: 実装内容、学習事項、テスト結果を記録する。

#### テスト

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

23件すべて成功した。すべてモックまたはFlaskテストクライアントによるテストであり、実Riot API通信は行っていない。

- MATCH-V5へ`queue=420`、`start=0`、`count=1`を渡す。
- URLのパス要素をエンコードする。
- `queueId=420`だけを受け入れる。
- PUUID一致participantから戦績を取得する。
- 通常KDAとDeath 0の暫定KDAを計算する。
- 試合0件をHTTP 200と`latestMatch: null`で返す。
- participant不在、必須項目欠損、型不正、負数を拒否する。
- 空欄、型不正、制御文字を含むRiot IDでAPIを呼ばない。
- STEP 1・2のApplication Factory、静的ファイル、JP1判定、HTTPエラー分類を維持する。
- テスト中に外部HTTP通信が発生しない。

#### 残る課題

- 実ブラウザでの結果カード、読み込み中、エラー、試合なし表示はSTEP 4で実装する。
- KDAの表示桁数とDeath 0時の画面文言はSTEP 4で決める。
- Riot IDの正式な文字数・許可文字の仕様は今回確定していないため、過剰な文字種制限は行っていない。
- 実APIでのqueue 420・戦績JSONの結合確認は未実施である。
- 20試合、他モード、MySQL、同期、キャッシュは今回の対象外である。

次はP1 STEP 4として、既存HTML・CSS・JavaScriptを活かし、読み込み中、戦績カード、エラー、Solo/Duo試合なしを画面へ表示する。

### 7.6 2026-11-05 P1 STEP 4 戦績カードの画面表示

STEP 3で`POST /search`から返せるようになったSolo/Duo最新1試合の戦績を、既存の検索フォームから実際のWeb画面へ表示できるようにした。外部ライブラリやチャンピオン画像は追加せず、HTML、CSS、JavaScriptだけで必要な表示と状態管理を実装した。

#### 実装した画面機能

- 検索したRiot IDを`gameName#tagline`形式で表示する。
- 「Solo/Duo 最新1試合」であることを明示する。
- チャンピオン名、WIN / LOSE、Kills、Deaths、Assists、KDAを戦績カードへ表示する。
- KDAはJavaScriptで小数点以下2桁に整形する。Serviceが返した計算値自体は変更しない。
- `zeroDeaths`が`true`の場合は、「0デスのため、KDAはKills + Assistsの値として表示しています。」という補足を表示する。
- APIから得た文字列は`textContent`でDOMへ設定し、HTMLとして挿入しない。

#### Flaskから画面までのデータの流れ

```text
検索フォーム
  gameNameとtaglineをJavaScriptがJSONへ変換
↓ POST /search
Blueprint
  JSONを受信し、PlayerSearchServiceを呼び出す
↓
Service / RiotApiClient
  PUUID取得 → JP1所属確認 → queue 420最新1試合 → 戦績とKDA
↓ JSONレスポンス
JavaScript
  HTTPステータスとJSON構造を確認し、安全にDOMへ反映
↓
戦績カード、試合なし案内、またはエラー案内
```

HTTPレスポンスの生成はBlueprint、取得順序とKDA計算はService、外部通信はRiotApiClient、表示状態と小数点以下2桁への整形はJavaScriptが担当する。

#### 画面状態の管理

画面では次の状態を同時に表示しないよう、JavaScriptの`showOnly`で切り替える。

1. 初期状態: 検索方法の案内を表示する。
2. 検索中: ローディング表示へ切り替え、検索ボタンを無効にする。
3. 取得成功: 戦績カードを表示する。
4. 試合なし: `latestMatch: null`を正常結果として扱い、「Solo/Duoランクの対象試合がありません」と表示する。
5. 入力エラー: 空欄などを画面側でも検出し、安全な案内を表示する。
6. API・通信エラー: サーバーの安全なメッセージを表示し、429、タイムアウト、APIキー問題などを区別する。

検索開始時に前回の戦績値を消し、失敗時にも結果カードを隠す。これにより、古い戦績を新しい検索結果と誤認しない。検索中はボタンを無効にして二重送信を防ぎ、処理終了時に必ず再び操作可能にする。

#### 安全性とデバッグ設定

- `response.ok`を確認してから正常データとして扱う。
- JSONを読み取れない場合や必須項目の型が違う場合も、画面を壊さず利用者向けエラーへ変換する。
- APIキー、PUUID、生レスポンス全文を画面やconsoleへ出力しない。
- `innerHTML`を使わず、取得データは`textContent`で反映する。
- `app.py`の`debug=True`固定を廃止し、`python app.py`ではデバッグモードを無効にした。デバッグモードは詳細な内部情報を表示する可能性があるため、必要なローカル開発時だけ明示的に有効化する。

#### 変更したファイル

- `templates/index.html`: 検索フォーム、各状態、戦績カードの構造を追加した。
- `static/css/style.css`: 戦績カード、WIN / LOSE、状態案内、ローディング、レスポンシブ表示を追加した。
- `static/js/main.js`: fetch、状態切り替え、JSON検証、DOM反映、エラー処理、二重送信防止を追加した。
- `app.py`: デバッグモードをデフォルト無効にした。
- `tests/test_app.py`: 画面要素、JavaScriptの安全なDOM更新、デバッグ既定値を確認するテストを追加した。
- `DEVELOPMENT.md`: STEP 4の実装、検証結果、学習事項を記録した。

#### 自動テスト結果

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

24件すべて成功した。Flaskテストクライアント、`unittest`、`unittest.mock`による確認であり、自動テスト中に実Riot API通信は行っていない。

- HTML、CSS、JavaScriptを読み込める。
- 正常検索でSTEP 4が利用するJSONを返す。
- 試合0件をHTTP 200と`latestMatch: null`で返す。
- エラーJSONにAPIキー、PUUID、生レスポンスを含めない。
- JavaScriptがHTTPステータスを確認し、`textContent`を使い、検索中にボタンを無効にするコードを含む。
- アプリの既定デバッグ設定が無効である。

JavaScriptの実際の描画やCSSの見た目はPythonの`unittest`だけでは完全には検証できないため、実ブラウザ確認と区別する。

#### 実ブラウザで確認したこと

ユーザーがローカル環境の`http://127.0.0.1:5000/`で実ブラウザ確認を行い、実際のRiot ID検索からSolo/Duo最新1試合の戦績カード表示まで成功した。

- チャンピオン: TwistedFate
- 勝敗: LOSE
- Kills: 2
- Deaths: 3
- Assists: 1
- 表示KDA: 1.00
- 計算確認: `(2 + 1) / 3 = 1.00`

これはユーザーが実ブラウザと実際の検索結果で確認した内容である。一方、試合なし、入力エラー、429、タイムアウト、APIキー問題、不正JSON、participant不在、Death 0などの異常系・境界値は、現時点では主にモックテストとコード確認による検証であり、実ブラウザでは未確認である。

#### 学んだこと

- HTMLは画面の構造、CSSは見た目、JavaScriptは状態とデータ反映を担当する。
- fetchはHTTP成功だけでなく`response.ok`とJSON構造も確認する必要がある。
- 非同期処理では、開始時・成功時・失敗時・終了時の状態を分けると古い表示や二重送信を防げる。
- `textContent`は、外部API由来の文字列をHTMLとして解釈させず表示する基本的な安全策になる。
- バックエンドでは精度を保ったKDAを返し、画面で`toFixed(2)`を使うと表示目的だけの丸めにできる。
- 自動テストと実ブラウザ確認は役割が異なり、両方の結果を混同せず記録する必要がある。

#### 今後の課題

- 実ブラウザで試合なし、0デス、入力エラー、429、タイムアウト、APIキー問題などを確認する。
- Riot IDの正式な文字数と許可文字は、公式仕様を確認してから検証条件を確定する。
- P1 STEP 5で、正常系と異常系の検証結果を整理し、P1の完成条件を最終確認する。
- 20試合、他モード、MySQL、同期、キャッシュ、改善目標、レビューはP1 STEP 4の対象外として引き続き実装しない。

### 7.7 2026-11-12 P1 STEP 5 最終検証・品質確認

P1の新機能は追加せず、STEP 1〜4で実装したRiot ID検索、JP1所属確認、Solo/Duo最新1試合、K/D/A・KDA、画面状態、外部APIエラー処理を最終検証した。過去に確認済みの実ブラウザ正常系は記録を引き継ぎ、今回は実Riot API通信とブラウザ自動操作を行っていない。

#### 確認した機能

- JP1確認後だけ、MATCH-V5へ`queue=420`、`start=0`、`count=1`を指定する。
- 試合詳細の`queueId=420`を再確認し、対象PUUIDのparticipantからチャンピオン、勝敗、K/D/Aを取得する。
- 通常KDAとDeath 0時の暫定KDAを安全に計算する。
- 試合0件をHTTP 200と`latestMatch: null`で返す。
- Riot IDの空欄・型不正・不存在、JP1未確認、401、403、429、タイムアウト、接続エラー、5xx、不正JSON、必須項目欠損、participant不在、queue不一致を安全なエラーとして扱う。
- エラーJSONへAPIキー、PUUID、外部APIの生レスポンスを含めない。
- 初期、検索中、成功、試合なし、入力エラー、APIエラーの画面状態を切り替える。
- 0デスの補足、古い検索結果の消去、二重送信防止、`textContent`による安全な表示を行う。

#### 発見した不具合と修正

1. APIキー未設定時の事前停止がなかった。
   - 修正前は、未設定値を認証ヘッダーへ渡してHTTP通信を開始しようとしていた。
   - `RiotConfigurationError`を追加し、キーが`None`、空文字、空白だけの場合は外部HTTP通信前にHTTP 503相当の安全なJSONエラーで停止するようにした。
   - キーの値や設定ファイルの内容はレスポンスへ含めない。
2. 二重送信防止がボタンの無効化だけに依存していた。
   - `isSearchInProgress`を追加し、検索中の連続submitイベントをJavaScript内部でも拒否するようにした。
   - `finally`で必ずフラグとボタン状態を戻す。

どちらも既存のApplication Factory、Blueprint、Service、Clientの境界とJSON形式を変えない最小限の修正である。

#### JavaScriptの実行テスト

Node.js v24.22.1が既存環境で利用できたため、追加ライブラリを導入せず、Node.js標準の`node:test`、`vm`、`assert`と小さなDOMモックで実際の`static/js/main.js`を実行するテストを追加した。

- 初期状態
- 検索中とボタン無効化
- 正常結果とKDA小数点以下2桁
- 試合なし
- Death 0の補足
- 空欄入力
- HTTP 429
- HTTP 504
- fetchの接続エラー
- 二重submitの拒否
- 古い結果の消去
- 不正JSON
- HTMLに見える文字列を`textContent`へ設定すること

このテストは文字列検索ではなく実際のJavaScriptを実行するが、簡易DOMモックであり、CSSの見た目や実ブラウザ固有の挙動を完全に保証するものではない。Node.jsがない環境ではPython側のテストをskipするため、新しい必須依存関係にはしていない。

#### テスト結果

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

29件すべて成功した。Node.jsの画面状態テストはPythonの1テストから起動し、内部の14テストもすべて成功した。すべてモックまたはFlaskテストクライアントによる検証であり、新しい実Riot API通信は行っていない。

追加した主な検証:

- APIキー未設定時にHTTP通信を行わず、安全な`riot_api_configuration_error`を返す。
- 401、403、タイムアウト、接続エラー、5xx相当、不正レスポンスが安全なJSONになる。
- `requests.ConnectionError`を無制限に再試行せず`RiotUnavailableError`へ分類する。
- 実際の`main.js`で画面状態、二重送信、古い結果、0デス、429、504、接続エラー、不正JSONを検証する。

#### 未確認項目

- 今回はブラウザ自動操作を再試行していない。
- 実ブラウザで確認済みなのは、ユーザーがSTEP 4で行った正常なRiot ID検索と戦績カード表示である。
- 試合なし、0デス、入力エラー、429、タイムアウト、APIキー未設定などは安全なモックで検証したが、実ブラウザでは未確認である。
- Riot IDの正式な文字数・許可文字と、非JP1の具体的なactive region値は引き続き未決定・未確認である。

#### 学んだこと

- 設定不足はHTTPライブラリの例外へ任せず、外部通信前に明示的に検証すると原因と安全な案内を分けやすい。
- ボタンの見た目上の無効化と、処理内部の多重実行ガードを併用すると二重送信に強くなる。
- Pythonテストから既存Node.jsを呼び出すことで、依存ライブラリを追加せずJavaScriptの状態遷移を実行検証できる。
- DOMモックテスト、Flaskテスト、実ブラウザ確認は検証範囲が異なるため、結果を区別して記録する必要がある。

#### P1完成条件

JP1所属アカウントをRiot IDで検索し、Solo/Duo最新1試合のチャンピオン、WIN / LOSE、Kills、Deaths、Assists、KDAをWeb画面へ表示する正常系は、ユーザーの実ブラウザ確認を含めて達成している。P1で必要な主要異常系もモックテストで安全に処理できることを確認した。

したがって、P1の実装とSTEP 5の品質確認は完了と判断できる。コミット、push、Pull Requestは、ユーザーとChatGPTの最終レビュー後に実施する。
