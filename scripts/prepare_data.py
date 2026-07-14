from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
NEO4J_DIR = ROOT / "data" / "neo4j"

LIST_FIELDS = {"AU", "AF", "C1", "C3", "CR", "EM", "RI", "OI"}
SEMICOLON_FIELDS = {"DE", "ID", "WC", "SC"}

FIELD_NAMES = {
    "PT": "publication_type",
    "AU": "authors_abbrev",
    "AF": "authors",
    "TI": "title",
    "SO": "source",
    "LA": "language",
    "DT": "document_type",
    "DE": "keywords",
    "ID": "keywords_plus",
    "AB": "abstract",
    "C1": "addresses",
    "C3": "institutions",
    "CR": "references",
    "PY": "year",
    "TC": "times_cited",
    "DI": "doi",
    "WC": "wos_categories",
    "SC": "research_areas",
    "UT": "wos_id",
}

SCHOOL_ALIASES = {
    "Sch Automat": "自动化学院",
    "Fac Automat": "自动化学院",
    "Coll Automat": "自动化学院",
    "Sch Mat & Energy": "材料与能源学院",
    "Sch Electromech Engn": "机电工程学院",
    "Fac Electromech Engn": "机电工程学院",
    "Sch Informat Engn": "信息工程学院",
    "Sch Phys & Optoelect Engn": "物理与光电工程学院",
    "Sch Management": "管理学院",
    "Sch Comp": "计算机学院",
    "Fac Comp": "计算机学院",
    "Sch Comp Sci & Technol": "计算机学院",
    "Sch Integrated Circuits": "集成电路学院",
    "Sch Math & Stat": "数学与统计学院",
    "Sch Art & Design": "艺术与设计学院",
    "Sch Chem Engn & Light Ind": "轻工化工学院",
    "Sch Environm Sci & Engn": "环境科学与工程学院",
    "Sch Civil & Transportat Engn": "土木与交通工程学院",
}


def split_semicolon(value: str) -> list[str]:
    return [item.strip(" .") for item in value.split(";") if item.strip(" .")]


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_wos(path: Path) -> list[dict[str, list[str]]]:
    records: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] = {}
    last_key: str | None = None

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw == "ER":
            if current:
                records.append(current)
            current = {}
            last_key = None
            continue

        if len(raw) >= 3 and re.match(r"^[A-Z0-9]{2} ", raw):
            key = raw[:2]
            value = normalize_spaces(raw[3:])
            current.setdefault(key, []).append(value)
            last_key = key
            continue

        if raw.startswith("   ") and last_key:
            value = normalize_spaces(raw)
            if not value:
                continue
            if last_key in LIST_FIELDS:
                current.setdefault(last_key, []).append(value)
            else:
                current[last_key][-1] = normalize_spaces(current[last_key][-1] + " " + value)

    if current:
        records.append(current)
    return records


def first(raw: dict[str, list[str]], key: str, default: str = "") -> str:
    values = raw.get(key) or []
    return values[0] if values else default


def all_values(raw: dict[str, list[str]], key: str) -> list[str]:
    values = raw.get(key) or []
    if key in SEMICOLON_FIELDS:
        result: list[str] = []
        for value in values:
            result.extend(split_semicolon(value))
        return result
    return [normalize_spaces(value) for value in values if normalize_spaces(value)]


def paper_id(raw: dict[str, list[str]], seq: int) -> str:
    wos_id = first(raw, "UT")
    if wos_id:
        return re.sub(r"[^A-Za-z0-9_:-]", "_", wos_id)
    doi = first(raw, "DI")
    if doi:
        return "DOI_" + re.sub(r"[^A-Za-z0-9_:-]", "_", doi)
    return f"PAPER_{seq:05d}"


def extract_school(addresses: list[str]) -> str:
    counts: Counter[str] = Counter()
    for address in addresses:
        match = re.search(r"Guangdong Univ Technol,\s*([^,.]+)", address, re.I)
        if match:
            raw = match.group(1).strip()
            for alias, school in SCHOOL_ALIASES.items():
                if alias.lower() == raw.lower():
                    counts[school] += 3
            if raw and not re.search(r"Guangzhou|Peoples|China", raw, re.I):
                counts[SCHOOL_ALIASES.get(raw, raw)] += 1
        for alias, school in SCHOOL_ALIASES.items():
            if re.search(re.escape(alias), address, re.I):
                counts[school] += 2
    return counts.most_common(1)[0][0] if counts else "未知学院"


def normalize_institutions(values: list[str], addresses: list[str]) -> list[str]:
    institutions: set[str] = set()
    for value in values:
        for item in split_semicolon(value):
            item = normalize_spaces(item)
            if not item:
                continue
            if item in {"Guangdong", "Technology", "University of", "Guangdong University of"}:
                continue
            if item == "University of Technology":
                item = "Guangdong University of Technology"
            institutions.add(item)
    if not institutions:
        for address in addresses:
            if re.search(r"Guangdong Univ Technol|Guangdong University of Technology", address, re.I):
                institutions.add("Guangdong University of Technology")
    return sorted(institutions)


def normalize_record(raw: dict[str, list[str]], seq: int) -> dict[str, Any]:
    addresses = all_values(raw, "C1")
    authors = all_values(raw, "AF") or all_values(raw, "AU")
    keywords = all_values(raw, "DE")
    keywords_plus = all_values(raw, "ID")
    institutions = normalize_institutions(raw.get("C3", []), addresses)
    year_text = first(raw, "PY")
    cited_text = first(raw, "TC", "0")

    try:
        year = int(year_text)
    except ValueError:
        year = None
    try:
        times_cited = int(cited_text)
    except ValueError:
        times_cited = 0

    title = first(raw, "TI")
    abstract = first(raw, "AB")
    source = first(raw, "SO")

    return {
        "paper_id": paper_id(raw, seq),
        "seq": seq,
        "wos_id": first(raw, "UT"),
        "doi": first(raw, "DI"),
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "authors_abbrev": all_values(raw, "AU"),
        "keywords": keywords,
        "keywords_plus": keywords_plus,
        "source": source,
        "journal": source,
        "document_type": first(raw, "DT"),
        "publication_type": first(raw, "PT"),
        "year": year,
        "times_cited": times_cited,
        "language": first(raw, "LA"),
        "institutions": institutions,
        "school": extract_school(addresses),
        "addresses": addresses,
        "references": all_values(raw, "CR"),
        "wos_categories": all_values(raw, "WC"),
        "research_areas": all_values(raw, "SC"),
        "vector_text": normalize_spaces(" ".join([title, abstract, "; ".join(keywords), "; ".join(keywords_plus)])),
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def build_summary(papers: list[dict[str, Any]]) -> dict[str, Any]:
    by_year = Counter(str(p["year"]) for p in papers if p.get("year"))
    by_school = Counter(p["school"] for p in papers)
    by_journal = Counter(p["journal"] for p in papers if p.get("journal"))
    by_keyword = Counter(k.lower() for p in papers for k in p.get("keywords", []))
    by_category = Counter(c for p in papers for c in p.get("wos_categories", []))
    cited_by_year: defaultdict[str, int] = defaultdict(int)
    for paper in papers:
        if paper.get("year"):
            cited_by_year[str(paper["year"])] += int(paper.get("times_cited") or 0)

    authors: defaultdict[str, dict[str, Any]] = defaultdict(lambda: {"papers": 0, "citations": 0, "years": []})
    for paper in papers:
        for author in paper.get("authors", []):
            item = authors[author]
            item["papers"] += 1
            item["citations"] += int(paper.get("times_cited") or 0)
            if paper.get("year"):
                item["years"].append(paper["year"])

    author_rows = []
    for author, item in authors.items():
        years = item["years"]
        author_rows.append({
            "author": author,
            "paper_count": item["papers"],
            "citation_count": item["citations"],
            "first_year": min(years) if years else None,
            "academic_age": (max(years) - min(years) + 1) if years else None,
        })
    author_rows.sort(key=lambda x: (x["paper_count"], x["citation_count"]), reverse=True)

    cooperation = Counter()
    for paper in papers:
        schools = sorted(set([paper.get("school", "未知学院")]))
        institutions = sorted(set(paper.get("institutions", [])))
        for left, right in combinations(institutions[:12], 2):
            cooperation[(left, right)] += 1

    return {
        "total_papers": len(papers),
        "total_authors": len(authors),
        "total_keywords": len(by_keyword),
        "total_journals": len(by_journal),
        "year_distribution": sorted([{"year": k, "count": v} for k, v in by_year.items()], key=lambda x: x["year"]),
        "citation_by_year": sorted([{"year": k, "citations": v} for k, v in cited_by_year.items()], key=lambda x: x["year"]),
        "school_distribution": [{"name": k, "count": v} for k, v in by_school.most_common(20)],
        "journal_distribution": [{"name": k, "count": v} for k, v in by_journal.most_common(20)],
        "keyword_distribution": [{"name": k, "count": v} for k, v in by_keyword.most_common(40)],
        "category_distribution": [{"name": k, "count": v} for k, v in by_category.most_common(20)],
        "top_authors": author_rows[:80],
        "cooperation_distribution": [
            {"source": left, "target": right, "count": count}
            for (left, right), count in cooperation.most_common(50)
        ],
    }


def build_neo4j_files(papers: list[dict[str, Any]]) -> None:
    authors: dict[str, dict[str, str]] = {}
    institutions: dict[str, dict[str, str]] = {}
    schools: dict[str, dict[str, str]] = {}
    keywords: dict[str, dict[str, str]] = {}
    journals: dict[str, dict[str, str]] = {}

    paper_rows = []
    wrote_rows = []
    affiliated_rows = []
    belongs_rows = []
    keyword_rows = []
    journal_rows = []
    coauthor_rows = []

    for paper in papers:
        paper_rows.append({
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "year": paper.get("year") or "",
            "times_cited": paper.get("times_cited") or 0,
            "doi": paper.get("doi") or "",
        })
        school = paper.get("school") or "未知学院"
        schools[school] = {"school_id": school, "name": school}

        journal = paper.get("journal") or "未知期刊"
        journals[journal] = {"journal_id": journal, "name": journal}
        journal_rows.append({"paper_id": paper["paper_id"], "journal_id": journal})

        for author in paper.get("authors", []):
            authors[author] = {"author_id": author, "name": author}
            wrote_rows.append({"author_id": author, "paper_id": paper["paper_id"]})
            belongs_rows.append({"author_id": author, "school_id": school})
            for institution in paper.get("institutions", []):
                institutions[institution] = {"institution_id": institution, "name": institution}
                affiliated_rows.append({"author_id": author, "institution_id": institution})

        for left, right in combinations(sorted(set(paper.get("authors", []))), 2):
            coauthor_rows.append({"author_a": left, "author_b": right, "paper_id": paper["paper_id"]})

        for keyword in paper.get("keywords", [])[:12]:
            key = keyword.lower()
            keywords[key] = {"keyword_id": key, "name": keyword}
            keyword_rows.append({"paper_id": paper["paper_id"], "keyword_id": key})

    write_csv(NEO4J_DIR / "papers.csv", paper_rows, ["paper_id", "title", "year", "times_cited", "doi"])
    write_csv(NEO4J_DIR / "authors.csv", list(authors.values()), ["author_id", "name"])
    write_csv(NEO4J_DIR / "institutions.csv", list(institutions.values()), ["institution_id", "name"])
    write_csv(NEO4J_DIR / "schools.csv", list(schools.values()), ["school_id", "name"])
    write_csv(NEO4J_DIR / "keywords.csv", list(keywords.values()), ["keyword_id", "name"])
    write_csv(NEO4J_DIR / "journals.csv", list(journals.values()), ["journal_id", "name"])
    write_csv(NEO4J_DIR / "rel_wrote.csv", wrote_rows, ["author_id", "paper_id"])
    write_csv(NEO4J_DIR / "rel_affiliated_with.csv", affiliated_rows, ["author_id", "institution_id"])
    write_csv(NEO4J_DIR / "rel_belongs_to.csv", belongs_rows, ["author_id", "school_id"])
    write_csv(NEO4J_DIR / "rel_has_keyword.csv", keyword_rows, ["paper_id", "keyword_id"])
    write_csv(NEO4J_DIR / "rel_published_in.csv", journal_rows, ["paper_id", "journal_id"])
    write_csv(NEO4J_DIR / "rel_coauthored.csv", coauthor_rows, ["author_a", "author_b", "paper_id"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Web of Science txt file")
    args = parser.parse_args()

    raw_records = parse_wos(Path(args.input))
    papers = [normalize_record(raw, index + 1) for index, raw in enumerate(raw_records)]
    papers = [paper for paper in papers if paper["title"]]
    summary = build_summary(papers)

    write_json(PROCESSED_DIR / "papers.json", papers)
    write_json(PROCESSED_DIR / "summary.json", summary)
    write_csv(
        PROCESSED_DIR / "papers_flat.csv",
        papers,
        ["paper_id", "title", "year", "times_cited", "journal", "school", "doi", "document_type"],
    )
    build_neo4j_files(papers)

    print(f"Parsed records: {len(raw_records)}")
    print(f"Valid papers: {len(papers)}")
    print(f"Processed data: {PROCESSED_DIR}")
    print(f"Neo4j CSV: {NEO4J_DIR}")


if __name__ == "__main__":
    main()
