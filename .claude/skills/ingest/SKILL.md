---
name: ingest
description: CCA、UAV、航空戦闘AI、自動運転・ロボット向け世界モデルとシミュレータの公開記事を構造化データと静的Wikiへ取り込む。
---

# Ingest

最初にルートの`CLAUDE.md`を最後まで読み、その掲載範囲、スキーマ、安全性、文章規約に従う。

1. URLが`data/news.json`に掲載済みでないか確認する。
2. 原文を取得し、タイトルだけでなく本文から関連性、発表日、主体、開発段階を確認する。
3. `data/news.json`の必須スキーマに従って追加する。
4. 推測、企業の宣伝表現、リアルタイムの配置・飛行・作戦情報を含めない。
5. `python3 tools/build_site.py`と`python3 tools/verify_wiki.py`を実行する。
6. `docs/wiki/log.md`へ追加件数を記録する。
7. 変更したデータと分類を報告する。コミットは明示的に依頼された場合だけ行う。
