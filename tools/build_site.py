#!/usr/bin/env python3
"""data/news.json から静的Wikiページ、検索索引、概念グラフを生成する。"""
import json
import os
from collections import defaultdict

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def write(name, text):
    path = os.path.join(DOCS, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def entry(item):
    tags = " / ".join(item["topics"])
    return (
        f'- **{item["date"]}** [{item["title"]}]({item["url"]})\n\n'
        f'  {item["summary_ja"]}\n\n'
        f'  出典: {item["source"]} / 状態: `{item["status"]}` / {tags}'
    )


def grouped_page(title, intro, field, news):
    groups = defaultdict(list)
    for item in news:
        for value in item[field]:
            groups[value].append(item)
    lines = [f"# {title}", "", intro]
    for value in sorted(groups, key=str.casefold):
        lines += ["", f"## {value}", ""]
        lines += [entry(x) for x in sorted(groups[value], key=lambda x: x["date"], reverse=True)]
    if not groups:
        lines += ["", "掲載情報はまだありません。"]
    return "\n".join(lines)


def main():
    news = sorted(load("news.json"), key=lambda x: (x["date"], x["id"]), reverse=True)
    sources = load("sources.json")

    write("recent.md", "\n".join([
        "# 最近の動き", "",
        "公開一次情報を中心に、CCA、UAV、航空戦闘AI、自律システム向け世界モデルとシミュレータの動きを新しい順に掲載します。",
        "", *[entry(x) for x in news]
    ]))
    write("programs.md", grouped_page(
        "プログラム", "各国の開発・調達プログラム別の時系列です。", "programs", news))
    write("companies.md", grouped_page(
        "企業", "開発企業別の発表と公的機関による関連発表です。企業発表は宣伝表現と確認済み事実を分けて扱います。", "companies", news))
    write("aircraft.md", grouped_page(
        "機体", "機体名称別の発表と開発段階です。試作名称と正式名称は別名として追跡します。", "aircraft", news))
    write("topics.md", grouped_page(
        "技術・政策トピック", "自律技術、試験、契約、政策などの話題別一覧です。", "topics", news))
    write("world-models.md", grouped_page(
        "世界モデル", "自動運転、自動制御、移動ロボット、航空自律システムに関係する世界モデルの一覧です。", "models", news))
    write("simulators.md", grouped_page(
        "シミュレータ", "学習、検証、合成データ生成、Sim-to-Realに使われるシミュレータの一覧です。", "simulators", news))

    source_lines = [
        "# 情報源", "",
        "定期巡回の対象です。掲載判断では一次情報を優先し、SNSは発見経路としてのみ扱います。", "",
        "| 情報源 | 種別 | 国・地域 | 優先度 |", "| --- | --- | --- | --- |"
    ]
    for source in sorted((x for x in sources if x.get("enabled")), key=lambda x: (x["priority"], x["name"])):
        source_lines.append(
            f'| [{source["name"]}]({source["url"]}) | {source["source_type"]} | '
            f'{", ".join(source["countries"])} | {source["priority"]} |')
    write("sources.md", "\n".join(source_lines))

    index = []
    for item in news:
        index.append({
            "t": item["title"], "u": item["url"], "a": item["summary_ja"],
            "p": "recent.html", "pt": "最近の動き",
            "s": " / ".join(item["domains"] + item["programs"] + item["companies"] +
                              item["aircraft"] + item["models"] + item["simulators"] + item["topics"]),
            "d": item["date"], "status": item["status"],
        })
    with open(os.path.join(DOCS, "search.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))

    categories = {
        "program": sorted({x for n in news for x in n["programs"]}),
        "company": sorted({x for n in news for x in n["companies"]}),
        "aircraft": sorted({x for n in news for x in n["aircraft"]}),
        "domain": sorted({x for n in news for x in n["domains"]}),
        "model": sorted({x for n in news for x in n["models"]}),
        "simulator": sorted({x for n in news for x in n["simulators"]}),
        "topic": sorted({x for n in news for x in n["topics"]}),
    }
    nodes = []
    edges = defaultdict(int)
    for kind, values in categories.items():
        for value in values:
            nodes.append({"id": f"{kind}:{value}", "label": value, "group": kind, "links": 0, "p": {
                "program": "programs.html", "company": "companies.html",
                "aircraft": "aircraft.html", "domain": "topics.html",
                "model": "world-models.html", "simulator": "simulators.html",
                "topic": "topics.html"}[kind]})
    by_id = {x["id"]: x for x in nodes}
    for item in news:
        ids = ([f'program:{x}' for x in item["programs"]] +
               [f'company:{x}' for x in item["companies"]] +
               [f'aircraft:{x}' for x in item["aircraft"]] +
               [f'domain:{x}' for x in item["domains"]] +
               [f'model:{x}' for x in item["models"]] +
               [f'simulator:{x}' for x in item["simulators"]] +
               [f'topic:{x}' for x in item["topics"]])
        for node_id in ids:
            by_id[node_id]["links"] += 1
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                edges[tuple(sorted((a, b)))] += 1
    graph = {"nodes": nodes, "edges": [
        {"a": a, "b": b, "w": w} for (a, b), w in sorted(edges.items())]}
    with open(os.path.join(DOCS, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, separators=(",", ":"))

    print(f"site data: news={len(news)} sources={len(sources)} nodes={len(nodes)}")


if __name__ == "__main__":
    main()
