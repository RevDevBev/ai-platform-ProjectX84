import os

from hybrid_search import hybrid
from reranker import rerank
from search import search

MODE = os.environ.get("RAG_RETRIEVER", "hybrid+rerank")


def retrieve(question, chunks, vectors, user_level, mode=None, pool=20, top_n=3):
    """Returns [(rerank_score, first_stage_score, chunk)], best first.
    The app needs reranker scores for the refusal threshold, so only reranked modes exist."""
    mode = mode or MODE
    if mode == "vector+rerank":
        candidates = search(question, chunks, vectors, k=pool, user_level=user_level)
    elif mode == "hybrid+rerank":
        fused = hybrid(question, chunks, vectors, user_level, pool=pool, top_n=pool)
        candidates = [(s, c) for s, c, _v, _b in fused]
    else:
        raise ValueError(f"unknown retriever mode: {mode}")
    return rerank(question, candidates, top_n=top_n)