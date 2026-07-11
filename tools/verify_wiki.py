#!/usr/bin/env python3
"""Autonomous Airpower Watchの構造化データと生成物を検査する。"""
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from urllib.parse import urlsplit, urlunsplit

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
STATUSES = {
    "research", "announced", "solicitation", "selected", "contracted",
    "prototype", "ground-test", "flight-test", "production", "delivered",
    "operational", "updated", "cancelled",
}
SOURCE_TYPES = {"government", "military", "research", "company", "media"}
CONFIDENCE = {"primary", "secondary"}
CITATION_SCAN = {"not-scanned", "partial", "scanned", "unavailable"}
CITATION_TYPES = {"source", "reference", "related", "self"}
ARRAY_FIELDS = {"countries", "domains", "organizations", "companies", "programs", "aircraft", "models", "simulators", "topics"}
REQUIRED = {
    "id", "title", "date", "url", "source", "source_type", *ARRAY_FIELDS,
    "status", "summary_ja", "confidence", "collected_at", "citation_scan_status", "citations",
}
problems = []


def load(name):
    path = os.path.join(DATA, name)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        problems.append(f"[{name}] 読み込み失敗: {e}")
        return []


def norm_url(value):
    p = urlsplit(value)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), p.query, ""))


news = load("news.json")
sources = load("sources.json")

ids = Counter(x.get("id") for x in news)
urls = Counter(norm_url(x.get("url", "")) for x in news)
for i, item in enumerate(news):
    label = item.get("id", f"index:{i}")
    missing = REQUIRED - set(item)
    if missing:
        problems.append(f"[{label}] 必須キー不足: {', '.join(sorted(missing))}")
        continue
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+", item["id"]):
        problems.append(f"[{label}] id形式が不正")
    try:
        date.fromisoformat(item["date"])
        if not item["id"].startswith(item["date"]):
            problems.append(f"[{label}] idとdateが不一致")
    except ValueError:
        problems.append(f"[{label}] date形式が不正: {item['date']}")
    try:
        date.fromisoformat(item["collected_at"])
    except ValueError:
        problems.append(f"[{label}] collected_at形式が不正: {item['collected_at']}")
    if not item["url"].startswith(("https://", "http://")):
        problems.append(f"[{label}] URLがHTTP(S)ではない")
    if item["status"] not in STATUSES:
        problems.append(f"[{label}] statusが不正: {item['status']}")
    if item["source_type"] not in SOURCE_TYPES:
        problems.append(f"[{label}] source_typeが不正: {item['source_type']}")
    if item["confidence"] not in CONFIDENCE:
        problems.append(f"[{label}] confidenceが不正: {item['confidence']}")
    if item["citation_scan_status"] not in CITATION_SCAN:
        problems.append(f"[{label}] citation_scan_statusが不正: {item['citation_scan_status']}")
    if not isinstance(item["citations"], list):
        problems.append(f"[{label}] citationsは配列でなければならない")
    else:
        citation_urls = Counter()
        for citation in item["citations"]:
            if not isinstance(citation, dict) or not {"url", "title", "type"} <= set(citation):
                problems.append(f"[{label}] citationの必須キー不足")
                continue
            if not citation["url"].startswith(("https://", "http://")):
                problems.append(f"[{label}] citation URLがHTTP(S)ではない")
            if citation["type"] not in CITATION_TYPES:
                problems.append(f"[{label}] citation typeが不正: {citation['type']}")
            citation_urls[norm_url(citation["url"])] += 1
        for citation_url, count in citation_urls.items():
            if count > 1:
                problems.append(f"[{label}] citation URL重複: {citation_url}")
    for field in ARRAY_FIELDS:
        if not isinstance(item[field], list) or any(not isinstance(x, str) or not x.strip() for x in item[field]):
            problems.append(f"[{label}] {field}は空でない文字列の配列でなければならない")
    if not item["topics"]:
        problems.append(f"[{label}] topicsが空")
    if not item["domains"]:
        problems.append(f"[{label}] domainsが空")
    if not item["summary_ja"].strip() or len(item["summary_ja"]) > 280:
        problems.append(f"[{label}] summary_jaは1〜280文字にする")

for value, count in ids.items():
    if value and count > 1:
        problems.append(f"[重複id] {value} ×{count}")
for value, count in urls.items():
    if value and count > 1:
        problems.append(f"[重複URL] {value} ×{count}")

source_ids = Counter(x.get("id") for x in sources)
for source in sources:
    label = source.get("id", "unknown")
    for key in ("id", "name", "url", "source_type", "countries", "topics", "priority", "enabled"):
        if key not in source:
            problems.append(f"[source:{label}] 必須キー不足: {key}")
    if source.get("source_type") not in SOURCE_TYPES:
        problems.append(f"[source:{label}] source_typeが不正")
for value, count in source_ids.items():
    if value and count > 1:
        problems.append(f"[情報源id重複] {value} ×{count}")

expected = {"recent.md", "programs.md", "companies.md", "aircraft.md", "topics.md", "world-models.md", "simulators.md", "sources.md", "search.json", "graph.json", "weekly.json", "citation-graph.json", "weekly.md", "citations.md"}
missing_outputs = sorted(x for x in expected if not os.path.exists(os.path.join(DOCS, x)))
if missing_outputs:
    problems.append(f"[生成物不足] {', '.join(missing_outputs)}")

print(f"検査対象: news={len(news)} sources={len(sources)}")
if problems:
    print(f"検出 {len(problems)} 件:")
    for problem in problems:
        print(" -", problem)
    sys.exit(1)
print("問題なし")
