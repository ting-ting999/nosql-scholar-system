from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.data_store import ROOT, author_profile, graph_preview, load_summary, search_papers


app = FastAPI(title="NoSQL Scholar Analytics", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = ROOT / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/summary")
def summary():
    return load_summary()


@app.get("/api/papers")
def papers(
    q: str = "",
    year: int | None = None,
    school: str = "",
    limit: int = Query(default=20, ge=1, le=100),
):
    return {"items": search_papers(q, year, school, limit)}


@app.get("/api/authors/{author_name}")
def author(author_name: str):
    return author_profile(author_name)


@app.get("/api/graph-preview")
def graph(
    view: str = "representative",
    limit: int = Query(default=80, ge=10, le=200),
):
    return graph_preview(view=view, limit=limit)


@app.post("/api/vector/build")
def rebuild_vector_index():
    from backend.vector_search import build_index

    return build_index()


@app.get("/api/vector/papers")
def vector_papers(q: str, top_k: int = Query(default=10, ge=1, le=30)):
    from backend.vector_search import search_similar_papers

    return search_similar_papers(q, top_k)


@app.get("/api/vector/authors")
def vector_authors(name: str, top_k: int = Query(default=8, ge=1, le=20)):
    from backend.vector_search import search_similar_authors

    return search_similar_authors(name, top_k)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "root": str(ROOT),
        "frontend": str(FRONTEND_DIR),
        "processed_exists": Path(ROOT / "data" / "processed" / "papers.json").exists(),
    }
