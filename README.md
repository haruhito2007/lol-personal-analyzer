# サモナーズノート（Summoner's Note）

League of Legends（LoL）の戦績を取得し、試合の振り返りと改善につなげるための個人向けWebアプリです。

> **開発状況：P1完成（2026-11-12）／v1.0全体は開発中**  
> リポジトリ名 `lol-personal-analyzer` はそのまま使用しています。

学校で学んでいるPython・Web開発・Git・データベースの知識を実際の制作物に活かす、学習兼ポートフォリオプロジェクトです。

## 現在できること（P1）

- Riot ID（ゲーム名・タグライン）からプレイヤーを検索
- Riot APIの所属情報を確認し、**JP1（日本サーバー）** のアカウントに限定
- **Solo/Duoランク（queue 420）の最新1試合** を取得
- チャンピオン名、WIN / LOSE、Kills / Deaths / Assists、KDAを戦績カードに表示
- 0デス時のKDA補足、試合なし・入力エラー・APIエラーの案内
- ローディング表示、検索中の二重送信防止、古い検索結果の消去

※ P1は最新**1試合**の表示です。20試合表示、DB保存、改善目標、試合レビューは今後の開発対象です。

## 技術構成

| 領域 | 技術 |
|---|---|
| バックエンド | Python、Flask（Application Factory / Blueprint） |
| Riot API通信 | requests、Riot ACCOUNT-V1 / MATCH-V5 |
| フロントエンド | HTML、CSS、JavaScript（Fetch API） |
| 設定 | python-dotenv（`.env`） |
| テスト | Python `unittest`、Node.js標準テスト機能 |

アプリ内部では、Flaskのルーティング・プレイヤー検索Service・Riot API Clientを分離しています。

## セットアップ（Windows / PowerShell）

### 1. クローンと仮想環境

```powershell
git clone https://github.com/haruhito2007/lol-personal-analyzer.git
cd lol-personal-analyzer
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Riot APIキーを設定

プロジェクト直下に `.env` を作成し、開発用APIキーを設定します。

```dotenv
RIOT_API_KEY=YOUR_RIOT_API_KEY
```

APIキーは[Riot Developer Portal](https://developer.riotgames.com/)で取得します。`.env` はGit管理対象外です。キーを変更した後はアプリを再起動してください。

### 3. 起動

```powershell
.\.venv\Scripts\python.exe app.py
```

ブラウザで `http://127.0.0.1:5000/` を開きます。`python app.py` ではデバッグモードは既定で無効です。

## テスト

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

P1最終確認時：Pythonテスト **29件成功**、Node.js UI状態テスト **14件成功**（skip 0）。

JavaScriptの実行テストは既存のNode.jsを使用します。Node.jsがない環境ではPythonから呼び出すUIテストがskipされます。テストはモックを使用し、実Riot APIへの通信は行いません。

## ディレクトリ構成

```text
lol-personal-analyzer/
├── app.py                     # Flask起動入口
├── summoners_note/            # 設定、Routes、Services、Riot API Client
├── templates/                 # HTML
├── static/                    # CSS / JavaScript
├── tests/                     # Python / JavaScriptテスト
├── docs/                      # 仕様・設計・開発記録
│   ├── REQUIREMENTS.md
│   ├── BASIC_DESIGN.md
│   ├── DATABASE.md
│   └── DEVELOPMENT.md
├── requirements.txt
├── .gitignore
└── README.md
```

## ドキュメント

| 文書 | 用途 |
|---|---|
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | v1.0の確定要件・対象範囲・開発優先順位 |
| [BASIC_DESIGN.md](docs/BASIC_DESIGN.md) | 承認済み基本設計の判断と未決定事項 |
| [DATABASE.md](docs/DATABASE.md) | DBの初期構想メモ（**未実装・未確定**） |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | 実装履歴・テスト・学習内容・エラーと解決 |

過去の実装段階を記録した文章には、当時の「次にやること」が残っています。**現在の実装状況はこのREADMEを優先**してください。

## ロードマップ

- **P1 完了**：JP1プレイヤー検索とSolo/Duo最新1試合の戦績表示（[PR #3](https://github.com/haruhito2007/lol-personal-analyzer/pull/3)）
- **P2 次の段階**：MySQL基盤と対象試合の同期
- **P3以降**：複数試合の履歴・統計、改善目標、試合レビュー、ダッシュボードの拡充

正式なv1.0の対象範囲と完成条件は [REQUIREMENTS.md](docs/REQUIREMENTS.md) を参照してください。

## 安全上の注意

- `.env`、APIキー、秘密鍵をコミットしないでください。
- 開発用Riot APIキーには使用条件・期限・レート制限があります。
- 本アプリは個人学習・開発用です。一般公開に向けた認証・運用は別途設計が必要です。
