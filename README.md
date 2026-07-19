# Autonomous Airpower Watch

CCA（Collaborative Combat Aircraft）、UAV、航空戦闘AI、および自動運転・自動制御・移動ロボットに関係する世界モデルとシミュレータの公開情報を追跡する静的Wikiです。

政府機関、軍、研究機関、開発企業の一次情報を優先し、短い日本語注釈と構造化メタデータをGitで管理します。記事本文は転載しません。

## 最近の更新

- [プロダクト] 2026-07-19: 操作ログからトップページの「最近の更新」を自動生成し、ニュース追加と機能更新を一緒に表示するよう変更
- [ニュース] 2026-07-18収集: 2026-07-15〜2026-07-16の新着3件（CCA 1件、航空戦闘AI 1件、世界モデル/シミュレータ 1件）を追加
- [プロダクト] 2026-07-11: データが少ない段階でも意味を読める「情報源→用途領域→開発段階」の週間ニュースフローを主表示に追加。引用グラフは実験ページへ移し、詳細カードをクリック固定式に修正
- [プロダクト] 2026-07-11: エンティティ共起マップを補助ページへ移し、収集日ベースの週間ダッシュボードと記事単位の引用・情報伝播グラフを追加。引用未調査と引用なしを区別するスキーマを導入
- [プロダクト] 2026-07-11: 週次収集をAnthropic Claude Code Actionから公式OpenAI Codex GitHub Actionへ移行。`OPENAI_API_KEY`と`gpt-5.4-mini`を使用
- [プロダクト] 2026-07-11: 対象を自動運転・自動制御・移動ロボット向けの世界モデル、シミュレータ、合成データ、Sim-to-Realへ拡張。用途領域、モデル、シミュレータのメタデータと概念マップを追加

## 目次

### ニュース

- [週間ダッシュボード](./docs/weekly.md): 収集数、カテゴリ、状態、新規エンティティを週単位で確認
- [週間ニュースフロー](./docs/flow.md): 情報源から用途領域、開発段階への流れを確認
- [最近の動き](./docs/recent.md): 公開情報を新しい順に確認
- [検索](./docs/search.md): タイトル、注釈、企業、プログラム、技術を横断検索

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
5. GitHub PagesがMarkdown、週間集計、検索索引、引用グラフを静的サイトとして公開します。

常駐サーバーとデータベースは使いません。収集に失敗しても、公開済みの静的サイトは影響を受けません。

定期実行は直近14日を重複確認するため、1回失敗しても次回に回収できます。手動実行では`lookback_days`を1〜90日で指定できます。

## OpenAI APIの設定

週次収集は公式の`openai/codex-action`からOpenAI Responses APIを利用します。GitHubリポジトリの`Settings` → `Secrets and variables` → `Actions`に、`OPENAI_API_KEY`という名前でOpenAI APIキーを登録してください。

ChatGPTの月額プランとOpenAI APIの利用枠・課金は別です。API Platformで利用可能なAPIキーと課金上限を設定してください。モデルは`.github/workflows/weekly-ingest.yml`で変更できます。

Actionsで`Quota exceeded`になった場合は、API Platformの残高、プロジェクト予算、利用上限を確認してください。設定後に`Weekly ingest`を手動実行すれば、指定期間を遡って収集します。

## ローカル確認

```bash
python3 tools/build_site.py
python3 tools/verify_wiki.py
```

生成対象は`docs/recent.md`、分類別ページ、週間集計、検索索引、引用グラフデータです。

データ蓄積を必要とする[引用・情報伝播グラフ](./docs/citations.md)と[エンティティ共起マップ](./docs/concept-map.md)は、実験的な補助ページとして残しています。共起マップの線は、引用や因果関係を示すものではありません。

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
