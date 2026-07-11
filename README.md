# Autonomous Airpower Watch

CCA（Collaborative Combat Aircraft）、UAV、航空戦闘AI、および自動運転・自動制御・移動ロボットに関係する世界モデルとシミュレータの公開情報を追跡する静的Wikiです。

政府機関、軍、研究機関、開発企業の一次情報を優先し、短い日本語注釈と構造化メタデータをGitで管理します。記事本文は転載しません。

## 最近の更新

- 2026-07-11: CCA/UAV向けの構造化データと静的Wiki生成基盤を作成

## 目次

### ニュース

- [最近の動き](./docs/recent.md): 公開情報を新しい順に確認
- [検索](./docs/search.md): タイトル、注釈、企業、プログラム、技術を横断検索
- [概念マップ](./docs/concept-map.md): 用途領域、企業、機体、世界モデル、シミュレータ、技術の関係を可視化

### 追跡対象

- [プログラム](./docs/programs.md): 開発・調達プログラム別の時系列
- [企業](./docs/companies.md): 開発企業別の動き
- [機体](./docs/aircraft.md): 機体名称別の開発状況
- [世界モデル](./docs/world-models.md): 自律システム向け世界モデル
- [シミュレータ](./docs/simulators.md): 学習、検証、合成データ生成、Sim-to-Real基盤
- [技術・政策トピック](./docs/topics.md): 自律技術、試験、契約、政策別の一覧
- [情報源](./docs/sources.md): 定期巡回する公開情報源

## 仕組み

1. GitHub Actionsが`data/sources.json`の公開情報源を定期確認します。
2. LLMが新着候補の本文を確認し、CCA、UAV、航空戦闘AI、または自律システム向け世界モデル・シミュレータとの関連性を判定します。
3. 掲載対象を`data/news.json`へ追加し、確認用Pull Requestを作成します。
4. 人間が日付、根拠、分類、表現を確認してマージします。
5. GitHub PagesがMarkdown、検索索引、概念マップを静的サイトとして公開します。

常駐サーバーとデータベースは使いません。収集に失敗しても、公開済みの静的サイトは影響を受けません。

## ローカル確認

```bash
python3 tools/build_site.py
python3 tools/verify_wiki.py
```

生成対象は`docs/recent.md`、分類別ページ、`docs/search.json`、`docs/graph.json`です。

## 編集方針

- 公開情報だけを扱います。
- 一次情報を優先し、企業発表では宣伝表現と確認済み事実を分けます。
- `announced`、`selected`、`contracted`、`prototype`、`flight-test`、`production`、`delivered`、`operational`を区別します。
- 公表されていない性能や運用能力を推測しません。
- リアルタイムの部隊配置、飛行位置、作戦情報は収集しません。
- 記事本文は保存せず、リンク、短い独自注釈、分類メタデータだけを保持します。

詳しいスキーマと運用規約は[CLAUDE.md](./CLAUDE.md)を参照してください。

## 来歴とライセンス

本プロジェクトは、MIT Licenseで公開されている[Everyday Kaggle News](https://github.com/upura/everyday-kaggle-news)の静的Wiki構成を基に、用途とデータモデルを再設計したものです。

ライセンスと著作権表示は[LICENSE](./LICENSE)を参照してください。
