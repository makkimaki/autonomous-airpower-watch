#!/usr/bin/env python3
"""構造化ニュースからWiki、週間集計、引用グラフを生成する。"""
import json
import os
from collections import Counter, defaultdict
from datetime import date, timedelta
from urllib.parse import urlsplit, urlunsplit

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
ENTITY_FIELDS = ("domains", "companies", "programs", "aircraft", "models", "simulators", "topics")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def write(name, text):
    with open(os.path.join(DOCS, name), "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def write_json(name, value):
    with open(os.path.join(DOCS, name), "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, separators=(",", ":"))


def norm_url(value):
    p = urlsplit(value)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), p.query, ""))


def week_start(value):
    day = date.fromisoformat(value)
    return (day - timedelta(days=day.weekday())).isoformat()


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


def count_values(items, field):
    return dict(sorted(Counter(value for item in items for value in item[field]).items(),
                       key=lambda x: (-x[1], x[0].casefold())))


def build_weekly(news):
    grouped = defaultdict(list)
    for item in news:
        grouped[week_start(item["collected_at"])].append(item)
    seen = {field: set() for field in ENTITY_FIELDS}
    weeks = []
    for start in sorted(grouped):
        items = sorted(grouped[start], key=lambda x: (x["collected_at"], x["date"], x["id"]), reverse=True)
        new_entities = {}
        for field in ENTITY_FIELDS:
            values = {value for item in items for value in item[field]}
            new_entities[field] = sorted(values - seen[field], key=str.casefold)
            seen[field].update(values)
        end = (date.fromisoformat(start) + timedelta(days=6)).isoformat()
        daily = Counter(item["collected_at"] for item in items)
        weeks.append({
            "start": start, "end": end, "count": len(items),
            "primary": sum(item["confidence"] == "primary" for item in items),
            "sources": len({item["source"] for item in items}),
            "domains": count_values(items, "domains"),
            "statuses": dict(Counter(item["status"] for item in items).most_common()),
            "source_types": dict(Counter(item["source_type"] for item in items).most_common()),
            "daily": dict(sorted(daily.items())),
            "topics": count_values(items, "topics"),
            "new_entities": new_entities,
            "article_ids": [item["id"] for item in items],
        })
    for i, week in enumerate(weeks):
        previous = weeks[i - 1]["count"] if i else 0
        week["previous_count"] = previous
        week["change"] = week["count"] - previous
    return {"weeks": list(reversed(weeks)), "latest": weeks[-1]["start"] if weeks else None}


def build_weekly_flow(news):
    """情報源→用途領域→開発段階の週間フローを生成する。"""
    grouped = defaultdict(list)
    for item in news:
        grouped[week_start(item["collected_at"])].append(item)
    weeks = []
    for start in sorted(grouped, reverse=True):
        items = grouped[start]
        node_articles = defaultdict(set)
        link_articles = defaultdict(set)
        articles = {}
        for item in items:
            articles[item["id"]] = {"id": item["id"], "title": item["title"], "url": item["url"],
                                     "date": item["date"], "summary": item["summary_ja"]}
            source_id = f'source:{item["source"]}'
            status_id = f'status:{item["status"]}'
            node_articles[source_id].add(item["id"])
            node_articles[status_id].add(item["id"])
            for domain in item["domains"]:
                domain_id = f'domain:{domain}'
                node_articles[domain_id].add(item["id"])
                link_articles[(source_id, domain_id)].add(item["id"])
                link_articles[(domain_id, status_id)].add(item["id"])
        labels = {"source": "情報源", "domain": "用途領域", "status": "開発段階"}
        nodes = []
        for node_id, article_ids in node_articles.items():
            kind, label = node_id.split(":", 1)
            nodes.append({"id": node_id, "kind": kind, "group": labels[kind], "label": label,
                          "value": len(article_ids), "articles": sorted(article_ids)})
        links = [{"source": a, "target": b, "value": len(ids), "articles": sorted(ids)}
                 for (a, b), ids in sorted(link_articles.items())]
        end = (date.fromisoformat(start) + timedelta(days=6)).isoformat()
        weeks.append({"start": start, "end": end, "nodes": nodes, "links": links,
                      "articles": list(articles.values())})
    return {"weeks": weeks, "latest": weeks[0]["start"] if weeks else None}


def find_cycles(adjacency):
    cycles = set()
    visiting, visited = set(), set()

    def walk(node, path):
        visiting.add(node)
        path.append(node)
        for target in adjacency.get(node, []):
            if target in visiting:
                cycle = path[path.index(target):] + [target]
                rotations = [tuple(cycle[i:-1] + cycle[:i] + [cycle[i]]) for i in range(len(cycle) - 1)]
                cycles.add(min(rotations))
            elif target not in visited:
                walk(target, path)
        path.pop()
        visiting.discard(node)
        visited.add(node)

    for node in adjacency:
        if node not in visited:
            walk(node, [])
    return [list(x) for x in sorted(cycles)]


def build_citation_graph(news):
    known = {norm_url(item["url"]): item for item in news}
    nodes = {}
    edges = []
    adjacency = defaultdict(list)
    for item in news:
        node_id = norm_url(item["url"])
        nodes[node_id] = {
            "id": node_id, "url": item["url"], "title": item["title"],
            "date": item["date"], "collected_at": item["collected_at"],
            "source": item["source"], "source_type": item["source_type"],
            "scan_status": item["citation_scan_status"], "external": False,
        }
    for item in news:
        source_id = norm_url(item["url"])
        for citation in item["citations"]:
            target_id = norm_url(citation["url"])
            if target_id not in nodes:
                nodes[target_id] = {
                    "id": target_id, "url": citation["url"], "title": citation["title"],
                    "date": "", "collected_at": "", "source": urlsplit(citation["url"]).netloc,
                    "source_type": "external", "scan_status": "not-scanned", "external": True,
                }
            edges.append({"source": source_id, "target": target_id, "type": citation["type"]})
            adjacency[source_id].append(target_id)
    indegree, outdegree = Counter(), Counter()
    for edge in edges:
        outdegree[edge["source"]] += 1
        indegree[edge["target"]] += 1
    for node_id, node in nodes.items():
        node["cited_by"] = indegree[node_id]
        node["cites"] = outdegree[node_id]
    ranked = sorted(nodes.values(), key=lambda x: (-x["cited_by"], x["title"].casefold()))
    roots = [x for x in ranked if x["cited_by"] and x["cites"] == 0 and x["scan_status"] == "scanned"]
    return {
        "nodes": list(nodes.values()), "edges": edges,
        "most_cited": [x["id"] for x in ranked if x["cited_by"]][:10],
        "root_candidates": [x["id"] for x in roots[:10]],
        "cycles": find_cycles(adjacency),
        "legend": {"source": "根拠・出典", "reference": "背景・技術資料", "related": "関連記事", "self": "同一サイト内"},
    }


def build_cooccurrence_graph(news):
    categories = {
        "program": sorted({x for n in news for x in n["programs"]}),
        "company": sorted({x for n in news for x in n["companies"]}),
        "aircraft": sorted({x for n in news for x in n["aircraft"]}),
        "domain": sorted({x for n in news for x in n["domains"]}),
        "model": sorted({x for n in news for x in n["models"]}),
        "simulator": sorted({x for n in news for x in n["simulators"]}),
        "topic": sorted({x for n in news for x in n["topics"]}),
    }
    pages = {"program": "programs.html", "company": "companies.html", "aircraft": "aircraft.html",
             "domain": "topics.html", "model": "world-models.html", "simulator": "simulators.html", "topic": "topics.html"}
    nodes = [{"id": f"{kind}:{value}", "label": value, "group": kind, "links": 0, "p": pages[kind]}
             for kind, values in categories.items() for value in values]
    by_id, edges = {x["id"]: x for x in nodes}, defaultdict(int)
    for item in news:
        ids = ([f'program:{x}' for x in item["programs"]] + [f'company:{x}' for x in item["companies"]] +
               [f'aircraft:{x}' for x in item["aircraft"]] + [f'domain:{x}' for x in item["domains"]] +
               [f'model:{x}' for x in item["models"]] + [f'simulator:{x}' for x in item["simulators"]] +
               [f'topic:{x}' for x in item["topics"]])
        for node_id in ids:
            by_id[node_id]["links"] += 1
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                edges[tuple(sorted((a, b)))] += 1
    return {"nodes": nodes, "edges": [{"a": a, "b": b, "w": w} for (a, b), w in sorted(edges.items())]}


def main():
    news = sorted(load("news.json"), key=lambda x: (x["date"], x["id"]), reverse=True)
    sources = load("sources.json")
    write("recent.md", "\n".join([
        "# 最近の動き", "",
        "公開一次情報を中心に、CCA、UAV、航空戦闘AI、自律システム向け世界モデルとシミュレータの動きを新しい順に掲載します。",
        "", *[entry(x) for x in news]
    ]))
    for filename, title, intro, field in (
        ("programs.md", "プログラム", "各国の開発・調達プログラム別の時系列です。", "programs"),
        ("companies.md", "企業", "開発企業別の発表と公的機関による関連発表です。", "companies"),
        ("aircraft.md", "機体", "機体名称別の発表と開発段階です。", "aircraft"),
        ("topics.md", "技術・政策トピック", "自律技術、試験、契約、政策などの話題別一覧です。", "topics"),
        ("world-models.md", "世界モデル", "自律システムに関係する世界モデルの一覧です。", "models"),
        ("simulators.md", "シミュレータ", "学習、検証、合成データ生成、Sim-to-Realに使われる基盤の一覧です。", "simulators"),
    ):
        write(filename, grouped_page(title, intro, field, news))

    source_lines = ["# 情報源", "", "定期巡回の対象です。一次情報を優先します。", "",
                    "| 情報源 | 種別 | 国・地域 | 優先度 |", "| --- | --- | --- | --- |"]
    for source in sorted((x for x in sources if x.get("enabled")), key=lambda x: (x["priority"], x["name"])):
        source_lines.append(f'| [{source["name"]}]({source["url"]}) | {source["source_type"]} | '
                            f'{", ".join(source["countries"])} | {source["priority"]} |')
    write("sources.md", "\n".join(source_lines))

    index = [{"t": x["title"], "u": x["url"], "a": x["summary_ja"], "p": "recent.html", "pt": "最近の動き",
              "s": " / ".join(x["domains"] + x["programs"] + x["companies"] + x["aircraft"] +
                                x["models"] + x["simulators"] + x["topics"]),
              "d": x["date"], "status": x["status"]} for x in news]
    write_json("search.json", index)
    write_json("weekly.json", build_weekly(news))
    write_json("weekly-flow.json", build_weekly_flow(news))
    write_json("citation-graph.json", build_citation_graph(news))
    graph = build_cooccurrence_graph(news)
    write_json("graph.json", graph)
    print(f"site data: news={len(news)} sources={len(sources)} cooccurrence_nodes={len(graph['nodes'])}")


if __name__ == "__main__":
    main()
