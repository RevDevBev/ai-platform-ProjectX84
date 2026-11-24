import math


def first_rank(labels, expected):
    """1-based rank of the first label that appears in `expected`, or None.
    `expected` is an any-of set: one correct chunk is enough."""
    ranks = [labels.index(e) + 1 for e in set(expected) if e in labels]
    return min(ranks) if ranks else None


def hit_at_k(labels, expected, k):
    rank = first_rank(labels, expected)
    return rank is not None and rank <= k


def reciprocal_rank(labels, expected):
    rank = first_rank(labels, expected)
    return 1.0 / rank if rank else 0.0


def recall_at_k(labels, required, k):
    """Fraction of the REQUIRED labels (all-of) found in the top k."""
    required = set(required)
    if not required:
        return None  # undefined: nothing was required
    return len(required & set(labels[:k])) / len(required)


def precision_at_k(labels, relevant, k):
    """Fraction of the top k that are relevant."""
    if k <= 0:
        return 0.0
    return sum(label in set(relevant) for label in labels[:k]) / k


def wilson_interval(successes, n, z=1.96):
    """95% interval for a proportion; behaves sensibly for small n."""
    if n == 0:
        return 0.0, 1.0
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, center - half), min(1.0, center + half)