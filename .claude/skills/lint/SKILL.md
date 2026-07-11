---
name: lint
description: 構造化ニュース、情報源、生成済み静的Wiki、外部リンクを検査する。
---

# Lint

1. `python3 tools/build_site.py`を実行する。
2. `python3 tools/verify_wiki.py`で必須キー、列挙値、日付、URL、重複、生成物を検査する。
3. 必要に応じて`python3 tools/check_external_links.py <report.md>`を実行する。
4. 検出結果を項目別に報告する。修正は管理者の確認後に行う。
