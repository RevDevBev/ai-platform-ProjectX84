import json
import os
import sys
from pathlib import Path

import numpy as np

from access import allowed_mask, masked_top_k
from embedder import embed_query

HERE = Path(__file__).parent
CANDIDATES = 20


def load_index():
    chunks = json.loads((HERE / "chunks.json").read_text(encoding="utf-8"))
    vectors = np.load(HERE / "index.npz")["vectors"]
    return chunks, vectors


def search(query, chunks, vectors, k=3, *, user_level):
    scores = vectors @embed_query(query)
    mask = allowed_mask(chunks, user_level)
    
    #mask = np.ones(len(chunks), dtype=bool)
    return [(float(scores[i]), chunks[i]) for i in masked_top_k(scores, mask, k)]


if __name__ == "__main__":
    from reranker import rerank

    level = os.environ.get("RAembed_queryG_USER_LEVEL", "public")
    question = " ".join(sys.argv[1:]) or "What happens to a message that fails three times?"
    chunks, vectors = load_index()
    candidates = search(question, chunks, vectors, k=min(CANDIDATES, len(chunks)), user_level=level)

    print(f"User level: {level}\n")
    print("First stage (embedding similarity), top 3:")
    for score, chunk in candidates[:3]:
        print(f"{score:.3f}  {chunk['id']}  [{chunk['section']}]  ({chunk['access']})")

    print("\nAfter cross-encoder reranking, top 3:")
    for rr_score, first_score, chunk in rerank(question, candidates, top_n=3):
        print(
            f"{rr_score:7.3f}  (was {first_score:.3f})  "
            f"{chunk['id']}  [{chunk['section']}]  ({chunk['access']})"
        )