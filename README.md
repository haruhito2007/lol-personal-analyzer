# LoL Personal Analyzer

League of Legends の戦績を取得・分析するWebアプリです。

学校で学習している Python / HTML / CSS / JavaScript / DB / Git / Linux などの技術を、実際のアプリ開発を通して活用することを目的に開発しています。

現在は Riot Games API を利用して、Riot IDからプレイヤー情報と直近試合の情報を取得する機能を実装しています。

## Features

現在実装済みの機能:

- Riot IDの入力フォーム
- JavaScriptからFlaskへのPOST通信
- Riot ACCOUNT-V1を利用したプレイヤー検索
- Riot IDからPUUIDを取得
- MATCH-V5を利用した直近20試合のMatch ID取得
- 最新試合の詳細データ取得
- 参加者10人の中からPUUIDを利用して本人を特定
- 最新試合で使用したChampionの取得

今後追加予定:

- Kills / Deaths / Assists の取得
- Win / Lose の取得
- KDAの計算
- Webページへの戦績表示
- 直近複数試合の分析
- 勝率
- 平均KDA
- CS
- Vision Score
- Champion別成績
- MySQLへの試合データ保存
- SQLを利用した戦績分析
- UI改善
- Linuxサーバーへのデプロイ

## Tech Stack

### Backend

- Python
- Flask

### Frontend

- HTML
- CSS
- JavaScript

### API

- Riot Games API
  - ACCOUNT-V1
  - MATCH-V5

### Python Libraries

- Flask
- requests
- python-dotenv

### Development

- Git
- GitHub
- VS Code
- Python Virtual Environment (`.venv`)

### Future

- MySQL
- Linux
- Web Server

## Application Flow

現在は以下の流れでデータを取得しています。

```text
ユーザーがRiot IDを入力
↓
HTMLフォーム
↓
JavaScriptでgameNameとtagLineを取得
↓
fetch()でFlaskの /search にPOST
↓
FlaskがJSONを受信
↓
Riot ACCOUNT-V1へアクセス
↓
PUUID取得
↓
MATCH-V5へアクセス
↓
直近20試合のMatch ID取得
↓
最新Match ID取得
↓
最新試合の詳細データ取得
↓
participantsから10人分のデータを取得
↓
PUUIDを比較して本人を特定
↓
使用Championを取得
```

## Project Structure

```text
lol-personal-analyzer/
├── app.py
├── README.md
├── DEVELOPMENT.md
├── requirements.txt
├── .gitignore
├── .env
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

`.env` と `.venv` はGitHubにはアップロードしません。

## Setup

### 1. Repositoryをclone

```bash
git clone <repository-url>
cd lol-personal-analyzer
```

### 2. Python仮想環境を作成

Windows:

```powershell
python -m venv .venv
```

仮想環境を有効化:

```powershell
.\.venv\Scripts\Activate.ps1
```

PowerShellのExecution Policyによって実行できない場合:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

その後、もう一度:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 必要なライブラリをインストール

```powershell
pip install -r requirements.txt
```

### 4. Riot API Keyを設定

プロジェクト直下に `.env` を作成します。

```env
RIOT_API_KEY=YOUR_RIOT_API_KEY
```

APIキーはRiot Developer Portalから取得します。

APIキーは秘密情報のため、ソースコードへ直接記述せず `.env` で管理しています。

`.gitignore` に `.env` を追加しているため、GitHubにはアップロードされません。

### 5. Flaskを起動

```powershell
python app.py
```

起動後、ブラウザで以下にアクセスします。

```text
http://127.0.0.1:5000
```

## Git Workflow

このプロジェクトはGit / GitHubでバージョン管理しています。

基本的な流れ:

```text
コードを変更
↓
git status
↓
git add
↓
git commit
↓
git push
↓
GitHubへ反映
```

2台のPCで開発しているため、別のPCで作業を開始するときは最初に、

```bash
git pull
```

を実行して最新状態を取得します。

## Development Status

現在開発中です。

現在は最新試合について、

```text
Riot ID
↓
PUUID
↓
Match ID
↓
試合詳細
↓
本人を特定
↓
Champion取得
```

まで実装しています。

次は、

```text
Kills
Deaths
Assists
Win / Lose
↓
KDA計算
↓
FlaskからJSONで返す
↓
JavaScriptで受信
↓
HTMLへ表示
```

を実装する予定です。

## Development Log

実装した内容、使用した技術、学んだこと、発生したエラーと解決方法については、

`DEVELOPMENT.md`

に記録しています。