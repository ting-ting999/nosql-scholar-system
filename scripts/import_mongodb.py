from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from pymongo import MongoClient, UpdateOne


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PAPERS_PATH = ROOT / "data" / "processed" / "papers.json"


def main() -> None:
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "nosql_scholar")
    client = MongoClient(uri)
    db = client[db_name]
    papers = json.loads(PAPERS_PATH.read_text(encoding="utf-8"))

    operations = [
        UpdateOne({"paper_id": paper["paper_id"]}, {"$set": paper}, upsert=True)
        for paper in papers
    ]
    if operations:
        result = db.papers.bulk_write(operations)
        print(f"upserted={result.upserted_count}, modified={result.modified_count}")

    db.papers.create_index("paper_id", unique=True)
    db.papers.create_index("year")
    db.papers.create_index("school")
    db.papers.create_index("authors")
    db.papers.create_index("keywords")
    db.papers.create_index([("title", "text"), ("abstract", "text"), ("keywords", "text")])
    print(f"MongoDB ready: {uri}/{db_name}, papers={db.papers.count_documents({})}")


if __name__ == "__main__":
    main()
