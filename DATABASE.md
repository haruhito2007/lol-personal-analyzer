# Database Design

## 1. 目的

Riot APIから取得したLoLの試合データをDBに保存し、
あとから以下のような分析をできるようにする。

- 勝率
- 平均KDA
- Champion別成績
- CS
- Vision Score
- 与ダメージ
- ゴールド
- ロール別成績


## 2. テーブル構成

今回は以下の3つのテーブルを使用する。

- players
- matches
- player_matches


## 3. players

プレイヤー自身の情報を保存するテーブル。

| カラム | 内容 |
|---|---|
| id | DB内部で使用するプレイヤーID |
| puuid | Riotがプレイヤーを識別するID |
| game_name | Riot IDのゲーム名 |
| tagline | Riot IDのタグライン |

### キー

id:
PRIMARY KEY

puuid:
UNIQUE

### 例

| id | puuid | game_name | tagline |
|---|---|---|---|
| 1 | 7-iI8ek... | Tanaka | JP1 |

`id` は自分たちのDB内部で使用する番号。

`puuid` はRiot側でプレイヤーを一意に識別するIDなので、
同じPUUIDを2回登録しないようにUNIQUEにする。


## 4. matches

試合そのものの情報を保存するテーブル。

| カラム | 内容 |
|---|---|
| id | DB内部で使用する試合ID |
| riot_match_id | Riot側のMatch ID |
| game_duration | 試合時間 |
| game_creation | 試合開始日時 |
| game_mode | ゲームモード |

### キー

id:
PRIMARY KEY

riot_match_id:
UNIQUE

### 例

| id | riot_match_id | game_duration | game_mode |
|---|---|---|---|
| 10 | JP1_604512428 | 1832 | CLASSIC |

`riot_match_id` は、

JP1_604512428

のようなRiot APIから取得した試合ID。

同じ試合を何度も保存しないためUNIQUEにする。


## 5. player_matches

「誰が、どの試合で、どんな成績だったか」を保存するテーブル。

| カラム | 内容 |
|---|---|
| id | この戦績データのID |
| player_id | どのプレイヤーか |
| match_id | どの試合か |
| champion_name | 使用Champion |
| kills | Kill数 |
| deaths | Death数 |
| assists | Assist数 |
| win | 勝敗 |
| cs | CS |
| vision_score | Vision Score |
| gold_earned | 獲得Gold |
| total_damage_dealt | 与ダメージ |
| role | ロール |

### キー

id:
PRIMARY KEY

player_id:
FOREIGN KEY → players.id

match_id:
FOREIGN KEY → matches.id

player_id と match_id の組み合わせ:
UNIQUE

同じプレイヤーの同じ試合データを、
2回保存しないようにする。


## 6. テーブル同士の関係

players

「誰なのか」

↓

player_matches

「その人がその試合でどうだったか」

↑

matches

「どの試合なのか」


例えば、

players:

id = 1
game_name = Slogan
tagline = BE2

matches:

id = 10
riot_match_id = JP1_604512428

player_matches:

player_id = 1
match_id = 10
champion_name = Ezreal
kills = 8
deaths = 3
assists = 10
win = True

となっていた場合、

「Tanaka#JP1 が JP1_604512428 という試合で
Ezrealを使用して 8 / 3 / 10 で勝利した」

という情報を表す。


## 7. PRIMARY KEY

PRIMARY KEYは、
テーブルの1行を一意に識別するための値。

今回の場合:

players.id
matches.id
player_matches.id

をPRIMARY KEYにする。


## 8. FOREIGN KEY

FOREIGN KEYは、
別のテーブルのデータを参照するための値。

player_matches.player_id

は、

players.id

を参照する。

つまり、

「この戦績は誰のものなのか」

を表す。


player_matches.match_id

は、

matches.id

を参照する。

つまり、

「この戦績はどの試合のものなのか」

を表す。


## 9. KDAについて

KDAそのものはDBには保存しない。

以下のデータだけ保存する。

- kills
- deaths
- assists

KDAが必要になったときに、

(kills + assists) / deaths

で計算する。

ただしdeathsが0の場合は0除算にならないように処理する。


## 10. アイテムについて

アイテムビルドも保存したいが、
最初のDB実装では一旦後回しにする。

将来的には、

player_match_items

という別テーブルを作り、

player_matches

と関連付ける予定。


## 11. 現在の構成

players
↓
player_matches
↑
matches

この3テーブルを最初のDB構成として使用する。


## 12. 今後追加する可能性があるデータ

今後の分析機能に応じて以下を追加する。

- Champion情報
- Item情報
- Damage情報
- CS/min
- KDA
- 勝率
- Champion別勝率
- Role別成績