import json
import sys
from pathlib import Path

import numpy as np

from embedder import embed_query

HERE = Path(__file__).parent


def load_index():
    chunks = json.loads((HERE / "chunks.json").read_text(encoding="utf-8"))
    vectors = np.load(HERE / "index.npz")["vectors"]
    return chunks, vectors


def search(query, chunks, vectors, k=3):
    scores = vectors @ embed_query(query)
    top = np.argsort(scores)[::-1][:k]
    return [(float(scores[i]), chunks[i]) for i in top]


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What happens to a message that fails three times?"
    chunks, vectors = load_index()
    for score, chunk in search(question, chunks, vectors):
        print(f"{score:.3f}  {chunk['id']}  [{chunk['section']}]  ({chunk['access']})")
        print("       " + chunk["text"].replace("\n", " ")[:110] + "...")