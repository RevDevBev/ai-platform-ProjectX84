import numpy as np

LEVELS = {"public": 0, "internal": 1, "restricted": 2}


def user_rank(user_level):
    # An unknown user level gets the least access.
    return LEVELS.get(user_level, 0)


def chunk_rank(chunk):
    # A missing or unknown label is treated as the most restricted.
    return LEVELS.get(chunk.get("access"), max(LEVELS.values()))


def allowed_mask(chunks, user_level):
    rank = user_rank(user_level)
    return np.array([chunk_rank(c) <= rank for c in chunks], dtype=bool)


def visible_chunks(chunks, user_level):
    mask = allowed_mask(chunks, user_level)
    return [c for c, ok in zip(chunks, mask) if ok]


def masked_top_k(scores, mask, k):
    """Indices of the k best-scoring ALLOWED items. Masked items can never be returned."""
    masked = np.where(mask, scores, -np.inf)
    order = np.argsort(masked)[::-1][:k]
    return [int(i) for i in order if np.isfinite(masked[i])]