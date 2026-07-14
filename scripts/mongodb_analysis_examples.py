from __future__ import annotations

import os
import sys
from pathlib import Path
from pprint import pprint

from pymongo import MongoClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = client[os.getenv("MONGODB_DB", "nosql_scholar")]


def show(title: str, pipeline):
    print("\n" + title)
    print("=" * len(title))
    pprint(list(db.papers.aggregate(pipeline)))


if __name__ == "__main__":
    show("年度发文趋势", [
        {"$match": {"year": {"$ne": None}}},
        {"$group": {"_id": "$year", "count": {"$sum": 1}, "citations": {"$sum": "$times_cited"}}},
        {"$sort": {"_id": 1}},
    ])
    show("学院发文量 Top 10", [
        {"$group": {"_id": "$school", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ])
    show("高频关键词 Top 20", [
        {"$unwind": "$keywords"},
        {"$group": {"_id": {"$toLower": "$keywords"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ])
    show("主要期刊 Top 15", [
        {"$group": {"_id": "$journal", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ])
