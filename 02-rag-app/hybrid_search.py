import os
import sys

from access import allowed_mask, user_rank, visible_chunks
from bm25_search import BM25Index
from fusion import rrf
from search import load_index, search

_BM25_BY_LEVEL = {}


def bm25_for(chunks, user_level):
    """One BM25 index per access level, built only from the chunks that level may see.
    Word statistics (IDF) are then never computed from text the user can't read."""
    key = user_rank(user_level)
    if key not in _BM25_BY_LEVEL:
        _BM25_BY_LEVEL[key] = BM25Index(visible_chunks(chunks, user_level))
    return _BM25_BY_LEVEL[key]


def hybrid(question, chunks, vectors, user_level, pool=20, k=60, top_n=10):
    """Returns [(fused_score, chunk, vector_rank, bm25_rank)], best first."""
    n = min(pool, int(allowed_mask(chunks, user_level).sum()))
    if n == 0:
        return []
    vec = [c for _s, c in search(question, chunks, vectors, k=n, user_level=user_level)]
    # A BM25 score of 0 means "no keyword evidence", so those chunks are left out.
    kw = [c for s, c in bm25_for(chunks, user_level).search(question, k=n) if s > 0]

    vec_rank = {c["id"]: r for r, c in enumerate(vec, 1)}
    kw_rank = {c["id"]: r for r, c in enumerate(kw, 1)}
    fused = rrf([vec, kw], k=k, top_n=top_n)
    return [
        (score, chunk, vec_rank.get(chunk["id"]), kw_rank.get(chunk["id"]))
        for score, chunk in fused
    ]


if __name__ == "__main__":
    level = os.environ.get("RAG_USER_LEVEL", "public")
    question = " ".join(sys.argv[1:]) or "What does ERR-4291 mean?"
    chunks, vectors = load_index()
    print(f"User level: {level}\n")
    print(f"{'fused':>7}  {'vec':>4}  {'bm25':>4}  chunk")
    for score, chunk, v, b in hybrid(question, chunks, vectors, level, top_n=5):
        print(
            f"{score:7.4f}  {v if v else '-':>4}  {b if b else '-':>4}  "
            f"{chunk['id']}  [{chunk['source']} > {chunk['section']}]  ({chunk['access']})"
        )