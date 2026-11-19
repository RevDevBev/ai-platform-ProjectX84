import json
import sys
from pathlib import Path

from bm25_search import BM25Index
from fusion import rrf
from search import load_index, search


def hybrid(question, chunks, vectors, bm25_index, pool=20, k=60, top_n=10):
    """Returns [(fused_score, chunk, vector_rank, bm25_rank)], best first."""
    n = min(pool, len(chunks))
    vec = [c for _s, c in search(question, chunks, vectors, k=n)]
    # A BM25 score of 0 means "no keyword evidence", so those chunks are left out.
    kw = [c for s, c in bm25_index.search(question, k=n) if s > 0]

    vec_rank = {c["id"]: r for r, c in enumerate(vec, 1)}
    kw_rank = {c["id"]: r for r, c in enumerate(kw, 1)}
    fused = rrf([vec, kw], k=k, top_n=top_n)
    return [
        (score, chunk, vec_rank.get(chunk["id"]), kw_rank.get(chunk["id"]))
        for score, chunk in fused
    ]


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What does ERR-4291 mean?"
    chunks, vectors = load_index()
    index = BM25Index(chunks)
    print(f"{'fused':>7}  {'vec':>4}  {'bm25':>4}  chunk")
    for score, chunk, v, b in hybrid(question, chunks, vectors, index, top_n=5):
        print(
            f"{score:7.4f}  {v if v else '-':>4}  {b if b else '-':>4}  "
            f"{chunk['id']}  [{chunk['source']} > {chunk['section']}]"
        )