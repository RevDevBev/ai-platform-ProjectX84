from functools import lru_cache

from fastembed.rerank.cross_encoder import TextCrossEncoder

RERANK_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def _encoder():
    return TextCrossEncoder(model_name=RERANK_MODEL)


def rerank(query, hits, top_n=3):
    """hits: list of (first_stage_score, chunk).
    Returns [(rerank_score, first_stage_score, chunk)], best first."""
    if not hits:
        return []
    scores = list(_encoder().rerank(query, [chunk["text"] for _, chunk in hits]))
    order = sorted(range(len(hits)), key=lambda i: scores[i], reverse=True)[:top_n]
    return [(float(scores[i]), hits[i][0], hits[i][1]) for i in order]