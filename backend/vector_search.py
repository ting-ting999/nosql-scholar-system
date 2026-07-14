from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.data_store import ROOT, author_research_texts, load_papers


FAISS_DIR = ROOT / "data" / "faiss"
VECTORIZER_PATH = FAISS_DIR / "tfidf_vectorizer.pkl"
MATRIX_PATH = FAISS_DIR / "paper_matrix.npy"
META_PATH = FAISS_DIR / "paper_meta.json"
FAISS_PATH = FAISS_DIR / "paper_faiss.index"


def _try_import_faiss():
    try:
        import faiss  # type: ignore

        return faiss
    except Exception:
        return None


def build_index(max_features: int = 12000) -> dict[str, Any]:
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    papers = load_papers()
    texts = [paper.get("vector_text") or paper.get("title", "") for paper in papers]
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
    )
    matrix_sparse = vectorizer.fit_transform(texts)
    matrix = matrix_sparse.astype(np.float32).toarray()
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    matrix = matrix / np.maximum(norms, 1e-12)

    pickle.dump(vectorizer, VECTORIZER_PATH.open("wb"))
    np.save(MATRIX_PATH, matrix)
    meta = [
        {
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "year": paper.get("year"),
            "authors": paper.get("authors", [])[:6],
            "journal": paper.get("journal"),
            "school": paper.get("school"),
            "keywords": paper.get("keywords", [])[:10],
            "times_cited": paper.get("times_cited", 0),
        }
        for paper in papers
    ]
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    faiss = _try_import_faiss()
    engine = "sklearn"
    if faiss is not None and matrix.size:
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        faiss.write_index(index, str(FAISS_PATH))
        engine = "faiss"

    return {"papers": len(papers), "dimension": int(matrix.shape[1]) if matrix.size else 0, "engine": engine}


def _load_index():
    if not VECTORIZER_PATH.exists() or not MATRIX_PATH.exists() or not META_PATH.exists():
        build_index()
    vectorizer = pickle.load(VECTORIZER_PATH.open("rb"))
    matrix = np.load(MATRIX_PATH)
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    return vectorizer, matrix, meta


def search_similar_papers(query: str, top_k: int = 10) -> dict[str, Any]:
    vectorizer, matrix, meta = _load_index()
    query_vec = vectorizer.transform([query]).astype(np.float32).toarray()
    norms = np.linalg.norm(query_vec, axis=1, keepdims=True)
    query_vec = query_vec / np.maximum(norms, 1e-12)

    faiss = _try_import_faiss()
    engine = "sklearn"
    if faiss is not None and FAISS_PATH.exists():
        index = faiss.read_index(str(FAISS_PATH))
        scores, indices = index.search(query_vec, top_k)
        pairs = [(int(idx), float(score)) for idx, score in zip(indices[0], scores[0]) if idx >= 0]
        engine = "faiss"
    else:
        scores = cosine_similarity(query_vec, matrix)[0]
        order = np.argsort(-scores)[:top_k]
        pairs = [(int(idx), float(scores[idx])) for idx in order]

    results = []
    for idx, score in pairs:
        item = dict(meta[idx])
        item["score"] = round(score, 4)
        results.append(item)
    return {"engine": engine, "query": query, "results": results}


def search_similar_authors(author_name: str, top_k: int = 8) -> dict[str, Any]:
    texts = author_research_texts()
    names = sorted(texts)
    target = next((name for name in names if name.lower() == author_name.lower()), None)
    if not target:
        candidates = [name for name in names if author_name.lower() in name.lower()][:20]
        return {"found": False, "candidates": candidates, "results": []}

    vectorizer = TfidfVectorizer(max_features=8000, stop_words="english", ngram_range=(1, 2), min_df=2)
    matrix = vectorizer.fit_transform([texts[name] for name in names]).astype(np.float32)
    target_index = names.index(target)
    scores = cosine_similarity(matrix[target_index], matrix)[0]
    order = [idx for idx in np.argsort(-scores) if idx != target_index][:top_k]
    return {
        "found": True,
        "author": target,
        "results": [{"author": names[idx], "score": round(float(scores[idx]), 4)} for idx in order],
    }
