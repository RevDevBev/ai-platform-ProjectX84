from collections import defaultdict


def rrf(rankings, k=60, top_n=10):
    """rankings: a list of ranked lists of chunks, each best first.
    Returns [(fused_score, chunk)], best first."""
    scores = defaultdict(float)
    by_id = {}
    for ranking in rankings:
        for rank, chunk in enumerate(ranking, start=1):
            scores[chunk["id"]] += 1.0 / (k + rank)
            by_id[chunk["id"]] = chunk
    ordered = sorted(scores, key=scores.get, reverse=True)[:top_n]
    return [(scores[i], by_id[i]) for i in ordered]