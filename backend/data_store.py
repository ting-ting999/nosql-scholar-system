from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
NEO4J_DIR = ROOT / "data" / "neo4j"
VECTOR_META_PATH = ROOT / "data" / "faiss" / "paper_meta.json"


@lru_cache(maxsize=1)
def load_papers() -> list[dict[str, Any]]:
    # The vector metadata contains every field needed by the Web API but is
    # much smaller than the full WOS document set. Prefer it in the server.
    if VECTOR_META_PATH.exists():
        return json.loads(VECTOR_META_PATH.read_text(encoding="utf-8"))
    return load_full_papers()


@lru_cache(maxsize=1)
def load_full_papers() -> list[dict[str, Any]]:
    path = PROCESSED_DIR / "papers.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_summary() -> dict[str, Any]:
    path = PROCESSED_DIR / "summary.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def search_papers(keyword: str = "", year: int | None = None, school: str = "", limit: int = 20) -> list[dict[str, Any]]:
    keyword_lower = keyword.strip().lower()
    results = []
    for paper in load_papers():
        if year and paper.get("year") != year:
            continue
        if school and paper.get("school") != school:
            continue
        if keyword_lower:
            haystack = " ".join([
                paper.get("title", ""),
                paper.get("abstract", ""),
                " ".join(paper.get("authors", [])),
                " ".join(paper.get("keywords", [])),
                paper.get("journal", ""),
            ]).lower()
            if keyword_lower not in haystack:
                continue
        results.append({
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "year": paper.get("year"),
            "authors": paper.get("authors", [])[:6],
            "journal": paper.get("journal"),
            "school": paper.get("school"),
            "times_cited": paper.get("times_cited", 0),
            "keywords": paper.get("keywords", [])[:8],
        })
        if len(results) >= limit:
            break
    return results


def author_profile(author_name: str) -> dict[str, Any] | None:
    name_lower = author_name.strip().lower()
    papers = [
        paper for paper in load_papers()
        if any(author.lower() == name_lower for author in paper.get("authors", []))
    ]
    if not papers:
        candidates = []
        for paper in load_papers():
            for author in paper.get("authors", []):
                if name_lower and name_lower in author.lower():
                    candidates.append(author)
        return {"found": False, "candidates": sorted(set(candidates))[:20]}

    keyword_counter = Counter(k.lower() for p in papers for k in p.get("keywords", []))
    coauthors = Counter()
    school_counter = Counter()
    journal_counter = Counter()
    citations = 0
    years = []
    for paper in papers:
        citations += int(paper.get("times_cited") or 0)
        if paper.get("year"):
            years.append(paper["year"])
        school_counter[paper.get("school", "未知学院")] += 1
        journal_counter[paper.get("journal", "未知期刊")] += 1
        for author in paper.get("authors", []):
            if author.lower() != name_lower:
                coauthors[author] += 1

    return {
        "found": True,
        "author": papers[0]["authors"][[a.lower() for a in papers[0]["authors"]].index(name_lower)],
        "paper_count": len(papers),
        "citation_count": citations,
        "first_year": min(years) if years else None,
        "latest_year": max(years) if years else None,
        "academic_age": (max(years) - min(years) + 1) if years else None,
        "top_keywords": [{"name": k, "count": v} for k, v in keyword_counter.most_common(15)],
        "top_coauthors": [{"name": k, "count": v} for k, v in coauthors.most_common(15)],
        "schools": [{"name": k, "count": v} for k, v in school_counter.most_common(8)],
        "journals": [{"name": k, "count": v} for k, v in journal_counter.most_common(8)],
        "papers": sorted([
            {
                "paper_id": p["paper_id"],
                "title": p["title"],
                "year": p.get("year"),
                "journal": p.get("journal"),
                "times_cited": p.get("times_cited", 0),
                "keywords": p.get("keywords", [])[:8],
            }
            for p in papers
        ], key=lambda item: (item["year"] or 0, item["times_cited"]), reverse=True)[:30],
    }


def graph_preview(limit: int = 80) -> dict[str, list[dict[str, Any]]]:
    papers = sorted(load_papers(), key=lambda p: int(p.get("times_cited") or 0), reverse=True)[:limit]
    nodes: dict[str, dict[str, Any]] = {}
    links: list[dict[str, Any]] = []

    def add_node(node_id: str, name: str, category: str, value: int = 1) -> None:
        if node_id not in nodes:
            nodes[node_id] = {"id": node_id, "name": name, "category": category, "value": value}

    for paper in papers:
        p_id = "paper:" + paper["paper_id"]
        add_node(p_id, paper["title"][:60], "Paper", int(paper.get("times_cited") or 1))
        for author in paper.get("authors", [])[:4]:
            a_id = "author:" + author
            add_node(a_id, author, "Author", 3)
            links.append({"source": a_id, "target": p_id, "name": "WROTE"})
        for keyword in paper.get("keywords", [])[:3]:
            k_id = "keyword:" + keyword.lower()
            add_node(k_id, keyword, "Keyword", 2)
            links.append({"source": p_id, "target": k_id, "name": "HAS_KEYWORD"})
        school = paper.get("school") or "未知学院"
        s_id = "school:" + school
        add_node(s_id, school, "School", 5)
        for author in paper.get("authors", [])[:4]:
            links.append({"source": "author:" + author, "target": s_id, "name": "BELONGS_TO"})

    return {"nodes": list(nodes.values()), "links": links}


@lru_cache(maxsize=1)
def load_author_school() -> dict[str, str]:
    path = NEO4J_DIR / "rel_belongs_to.csv"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return {row["author_id"]: row["school_id"] for row in csv.DictReader(file)}


@lru_cache(maxsize=1)
def load_coauthor_edges() -> list[tuple[str, str, str]]:
    path = NEO4J_DIR / "rel_coauthored.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [(row["author_a"], row["author_b"], row["paper_id"]) for row in csv.DictReader(file)]


def add_graph_node(nodes: dict[str, dict[str, Any]], node_id: str, name: str, category: str, value: int = 1) -> None:
    if node_id not in nodes:
        nodes[node_id] = {"id": node_id, "name": name, "category": category, "value": value}
    else:
        nodes[node_id]["value"] = max(nodes[node_id].get("value", 1), value)


def make_graph_response(
    *,
    title: str,
    description: str,
    cypher: str,
    categories: list[str],
    nodes: dict[str, dict[str, Any]],
    links: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "title": title,
        "description": description,
        "cypher": cypher.strip(),
        "categories": categories,
        "nodes": list(nodes.values()),
        "links": links,
    }


def graph_preview(view: str = "representative", limit: int = 80) -> dict[str, Any]:
    if view == "coauthor":
        return coauthor_graph(limit)
    if view == "keyword_author":
        return keyword_author_graph(limit)
    if view == "school_coop":
        return school_coop_graph(limit)
    if view == "shortest_path":
        return shortest_path_graph()
    return representative_graph(limit)


def representative_graph(limit: int = 80) -> dict[str, Any]:
    papers = sorted(load_papers(), key=lambda p: int(p.get("times_cited") or 0), reverse=True)[:limit]
    nodes: dict[str, dict[str, Any]] = {}
    links: list[dict[str, Any]] = []
    for paper in papers:
        p_id = "paper:" + paper["paper_id"]
        add_graph_node(nodes, p_id, paper["title"][:60], "Paper", int(paper.get("times_cited") or 1))
        for author in paper.get("authors", [])[:4]:
            a_id = "author:" + author
            add_graph_node(nodes, a_id, author, "Author", 3)
            links.append({"source": a_id, "target": p_id, "name": "WROTE"})
        for keyword in paper.get("keywords", [])[:3]:
            k_id = "keyword:" + keyword.lower()
            add_graph_node(nodes, k_id, keyword, "Keyword", 2)
            links.append({"source": p_id, "target": k_id, "name": "HAS_KEYWORD"})
        school = paper.get("school") or "未知学院"
        s_id = "school:" + school
        add_graph_node(nodes, s_id, school, "School", 5)
        for author in paper.get("authors", [])[:4]:
            links.append({"source": "author:" + author, "target": s_id, "name": "BELONGS_TO"})

    return make_graph_response(
        title="代表性子图展示",
        description="选取高被引论文及其作者、关键词、学院节点，展示论文对象如何连接多类实体。",
        categories=["Author", "Paper", "Keyword", "School"],
        nodes=nodes,
        links=links,
        cypher="""
MATCH (p:Paper)
WITH p ORDER BY p.times_cited DESC LIMIT 80
MATCH (a:Author)-[:WROTE]->(p)
OPTIONAL MATCH (p)-[:HAS_KEYWORD]->(k:Keyword)
OPTIONAL MATCH (a)-[:BELONGS_TO]->(s:School)
RETURN p, a, k, s;
""",
    )


def coauthor_graph(limit: int = 80) -> dict[str, Any]:
    pair_counts = Counter()
    node_counts = Counter()
    for author_a, author_b, _paper_id in load_coauthor_edges():
        key = tuple(sorted((author_a, author_b)))
        pair_counts[key] += 1
        node_counts[author_a] += 1
        node_counts[author_b] += 1

    nodes: dict[str, dict[str, Any]] = {}
    links: list[dict[str, Any]] = []
    for (author_a, author_b), count in pair_counts.most_common(limit):
        a_id = "author:" + author_a
        b_id = "author:" + author_b
        add_graph_node(nodes, a_id, author_a, "Author", node_counts[author_a])
        add_graph_node(nodes, b_id, author_b, "Author", node_counts[author_b])
        links.append({"source": a_id, "target": b_id, "name": f"COAUTHORED {count}", "value": count})

    return make_graph_response(
        title="学者合作网络",
        description="节点为作者，连线表示两位作者共同发表过论文，连线权重为合作论文数量。",
        categories=["Author"],
        nodes=nodes,
        links=links,
        cypher="""
MATCH (a1:Author)-[:COAUTHORED]-(a2:Author)
WHERE a1.name < a2.name
RETURN a1, a2, count(*) AS 合作次数
ORDER BY 合作次数 DESC
LIMIT 80;
""",
    )


def keyword_author_graph(limit: int = 80) -> dict[str, Any]:
    top_keywords = {item["name"].lower() for item in load_summary().get("keyword_distribution", [])[:8]}
    pair_counts = Counter()
    author_counts = Counter()
    keyword_counts = Counter()
    for paper in load_papers():
        keywords = [keyword.lower() for keyword in paper.get("keywords", []) if keyword.lower() in top_keywords]
        if not keywords:
            continue
        for author in paper.get("authors", [])[:6]:
            author_counts[author] += 1
            for keyword in keywords[:4]:
                pair_counts[(author, keyword)] += 1
                keyword_counts[keyword] += 1

    nodes: dict[str, dict[str, Any]] = {}
    links: list[dict[str, Any]] = []
    for (author, keyword), count in pair_counts.most_common(limit):
        a_id = "author:" + author
        k_id = "keyword:" + keyword
        add_graph_node(nodes, a_id, author, "Author", author_counts[author])
        add_graph_node(nodes, k_id, keyword, "Keyword", keyword_counts[keyword])
        links.append({"source": a_id, "target": k_id, "name": f"HAS_TOPIC {count}", "value": count})

    return make_graph_response(
        title="关键词与作者关联网络",
        description="节点包含高频关键词和相关作者，连线表示作者论文中出现该研究主题。",
        categories=["Author", "Keyword"],
        nodes=nodes,
        links=links,
        cypher="""
MATCH (k:Keyword)<-[:HAS_KEYWORD]-(p:Paper)<-[:WROTE]-(a:Author)
WHERE k.name IN ["deep learning", "optimization", "feature extraction"]
RETURN k, a, count(p) AS 相关论文数
ORDER BY 相关论文数 DESC
LIMIT 80;
""",
    )


def school_coop_graph(limit: int = 50) -> dict[str, Any]:
    author_school = load_author_school()
    pair_counts = Counter()
    school_counts = Counter()
    for author_a, author_b, _paper_id in load_coauthor_edges():
        school_a = author_school.get(author_a)
        school_b = author_school.get(author_b)
        if not school_a or not school_b or school_a == school_b:
            continue
        key = tuple(sorted((school_a, school_b)))
        pair_counts[key] += 1
        school_counts[school_a] += 1
        school_counts[school_b] += 1

    nodes: dict[str, dict[str, Any]] = {}
    links: list[dict[str, Any]] = []
    for (school_a, school_b), count in pair_counts.most_common(limit):
        a_id = "school:" + school_a
        b_id = "school:" + school_b
        add_graph_node(nodes, a_id, school_a, "School", school_counts[school_a])
        add_graph_node(nodes, b_id, school_b, "School", school_counts[school_b])
        links.append({"source": a_id, "target": b_id, "name": f"COOPERATES {count}", "value": count})

    return make_graph_response(
        title="学院合作关系图",
        description="节点为学院，连线表示不同学院作者在同一论文中发生合作，权重越大表示跨学院合作越频繁。",
        categories=["School"],
        nodes=nodes,
        links=links,
        cypher="""
MATCH (s1:School)<-[:BELONGS_TO]-(a1:Author)-[:WROTE]->(p:Paper)<-[:WROTE]-(a2:Author)-[:BELONGS_TO]->(s2:School)
WHERE s1.name < s2.name
RETURN s1, s2, count(DISTINCT p) AS 合作论文数
ORDER BY 合作论文数 DESC
LIMIT 50;
""",
    )


def shortest_path_graph() -> dict[str, Any]:
    adjacency: defaultdict[str, set[str]] = defaultdict(set)
    edge_weight = Counter()
    for author_a, author_b, _paper_id in load_coauthor_edges():
        adjacency[author_a].add(author_b)
        adjacency[author_b].add(author_a)
        edge_weight[tuple(sorted((author_a, author_b)))] += 1

    candidates = [author for author, _neighbors in sorted(adjacency.items(), key=lambda item: len(item[1]), reverse=True)[:80]]
    path: list[str] = []
    for start in candidates[:20]:
        queue: list[list[str]] = [[start]]
        visited = {start}
        while queue and not path:
            current_path = queue.pop(0)
            if len(current_path) >= 5:
                path = current_path
                break
            for neighbor in sorted(adjacency[current_path[-1]]):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                queue.append(current_path + [neighbor])
        if path:
            break
    if not path and candidates:
        first = candidates[0]
        path = [first] + sorted(adjacency[first])[:1]

    nodes: dict[str, dict[str, Any]] = {}
    links: list[dict[str, Any]] = []
    for index, author in enumerate(path):
        add_graph_node(nodes, "author:" + author, author, "Author", 10 - index)
    for author_a, author_b in zip(path, path[1:]):
        count = edge_weight[tuple(sorted((author_a, author_b)))]
        links.append({"source": "author:" + author_a, "target": "author:" + author_b, "name": f"COAUTHORED {count}", "value": count})

    start = path[0] if path else "Author A"
    end = path[-1] if path else "Author B"
    return make_graph_response(
        title="最短合作路径分析",
        description=f"示例展示 {start} 与 {end} 之间的合作链路，用于说明图数据库的路径查询能力。",
        categories=["Author"],
        nodes=nodes,
        links=links,
        cypher=f"""
MATCH path = shortestPath(
  (a:Author {{name: "{start}"}})-[:COAUTHORED*..6]-(b:Author {{name: "{end}"}})
)
RETURN path;
""",
    )


def author_research_texts() -> dict[str, str]:
    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for paper in load_papers():
        text = " ".join([
            paper.get("title", ""),
            paper.get("abstract", ""),
            " ".join(paper.get("keywords", [])),
        ])
        for author in paper.get("authors", []):
            grouped[author].append(text)
    return {author: " ".join(texts[:20]) for author, texts in grouped.items() if len(texts) >= 2}
