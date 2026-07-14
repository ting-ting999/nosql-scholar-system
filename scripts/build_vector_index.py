from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.vector_search import build_index


if __name__ == "__main__":
    result = build_index()
    print(result)
