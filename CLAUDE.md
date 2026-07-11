# Autonomous Airpower Watch 運用規約

本リポジトリは、CCA、UAV、航空戦闘AIと、自動運転・自動制御・移動ロボットに関係する世界モデルおよびシミュレータの公開情報を、人間のレビューを介して静的Wikiへ反映します。

## データ層

- `data/sources.json`: 定期巡回する公開情報源
- `data/news.json`: 掲載するニュース、収集日、本文中の引用・参照リンクを含む正規化済みメタデータ
- `docs/*.md`: `tools/build_site.py`が生成する閲覧ページ
- `docs/wiki/log.md`: 収集・構成変更・検査の記録

記事本文は保存しません。URL、書誌情報、短い独自注釈、分類だけを保持します。

## 掲載範囲

- Collaborative Combat Aircraft、Loyal Wingman、UCAV
- 軍用UAVと有人・無人協調
- 航空機向けミッション自律、空戦AI、群制御、センサーフュージョン
- 関連する調達、契約、予算、試験、国際共同開発
- 上記を開発する企業、政府機関、研究機関の動向
- 自動運転車、移動ロボット、無人航空機の認識・予測・計画・制御に使う世界モデル
- 自律システムの学習、検証、合成データ生成、デジタルツイン、Sim-to-Realに使うシミュレータ

民生ドローンのみの記事、兵器搭載と関係しない一般AI記事、根拠のない噂は対象外です。

## news.jsonスキーマ

各要素は次のキーを必須とします。

- `id`: `YYYY-MM-DD-slug`形式の一意な識別子
- `title`, `date`, `collected_at`, `url`, `source`, `source_type`
- `countries`, `domains`, `organizations`, `companies`, `programs`, `aircraft`, `models`, `simulators`, `topics`: 文字列配列
- `status`: 開発・調達段階
- `summary_ja`: 原文を確認して書いた1〜2文の独自注釈
- `confidence`: `primary`または`secondary`
- `citation_scan_status`: `not-scanned`、`partial`、`scanned`、`unavailable`
- `citations`: 記事本文で確認できた参照リンクの配列。各要素は`url`、`title`、`type`を持つ

`citations[].type`は`source`（根拠・出典）、`reference`（背景・技術資料）、`related`（関連記事）、`self`（同一サイト内）から選びます。ナビゲーション、広告、SNS共有、製品ページへの単なる導線は含めません。

`status`は原則として次から選びます。

`research` / `announced` / `solicitation` / `selected` / `contracted` / `prototype` / `ground-test` / `flight-test` / `production` / `delivered` / `operational` / `updated` / `cancelled`

## 取り込み規約

1. `data/sources.json`の有効な情報源を確認します。
2. URLを正規化し、`data/news.json`との重複を除きます。
3. 原文を取得し、掲載範囲との関係を本文で確認します。タイトルだけで判定しません。
4. 発表日と出来事の発生日を混同しません。`date`は原則として発表日です。
5. 発表、選定、契約、試験、量産、配備を区別します。
6. 一次情報にない性能、意図、実戦能力を推測しません。
7. `collected_at`にWikiへ追加した日を記録します。
8. 記事本文の引用・参照を確認し、調査状態と`citations`を記録します。取得不能なら`unavailable`、一部だけ確認できた場合は`partial`にします。
9. `summary_ja`は短い独自表現とし、本文を転載しません。
10. `python3 tools/build_site.py`と`python3 tools/verify_wiki.py`を実行します。
11. `docs/wiki/log.md`へ取り込み件数と対象期間を記録します。

## 情報源の扱い

- 政府、軍、研究機関、企業の公式発表を一次情報として優先します。
- 報道記事は一次情報で不足する背景の補完に使い、`confidence`を`secondary`にします。
- SNSは候補の発見に使えますが、SNS投稿だけを根拠に掲載しません。
- 企業発表の評価的表現を、確認済みの性能として書き換えません。
- 契約上限額、予算要求額、実際の発注額を区別します。

## 公開情報と安全性

- 公開済みの情報だけを扱います。
- リアルタイムまたは準リアルタイムの部隊配置、飛行位置、作戦行動を掲載しません。
- 複数の公開情報を組み合わせて、非公表の能力や運用を推定しません。
- 訂正、延期、中止が公表された場合は、過去記事を消さず更新情報を追加します。

## 人間によるレビュー

自動取り込みは必ずPull Requestにします。マージ前に、URL、日付、固有名詞、開発段階、注釈の根拠、安全性を確認します。

## 文章規約

- 日本語の文中の括弧は全角（）を使います。
- 固有名詞は公式表記を優先し、旧称と正式名称を勝手に統合しません。
- CCA、UAV、UCAV、MUM-T、autonomous、AI-enabledを同義語として扱いません。
- 「世界モデル」は環境の状態や時間変化を学習・予測するモデルを指し、3D表示基盤や物理シミュレータと区別します。
- 自動運転は道路車両、移動ロボットは地上・屋内外ロボット、自動制御は対象システムを`domains`で明示します。
