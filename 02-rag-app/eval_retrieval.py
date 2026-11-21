import json
import random
import time
from pathlib import Path

from bm25_search import BM25Index
from hybrid_search import hybrid
from reranker import rerank
from search import load_index, search

HERE = Path(__file__).parent
QUESTIONS = json.loads((HERE / "eval" / "questions.json").read_text(encoding="utf-8"))
EVAL_LEVEL = "restricted"  # offline quality measurement: the evaluator sees everything
DEPTH = 10

chunks, vectors = load_index()
bm25_index = BM25Index(chunks)


def label(chunk):
    return f"{chunk['source']} > {chunk['section']}"


def vector_only(q):
    return [c for _s, c in search(q, chunks, vectors, k=DEPTH, user_level=EVAL_LEVEL)]


def bm25_only(q):
    # Zero-score chunks are "no keyword evidence", so they are not results.
    return [c for s, c in bm25_index.search(q, k=DEPTH) if s > 0]


def hybrid_only(q):
    return [c for _s, c, _v, _b in hybrid(q, chunks, vectors, EVAL_LEVEL, top_n=DEPTH)]


def vector_rerank(q):
    cands = search(q, chunks, vectors, k=min(20, len(chunks)), user_level=EVAL_LEVEL)
    return [c for _rr, _f, c in rerank(q, cands, top_n=DEPTH)]


def hybrid_rerank(q):
    fused = hybrid(q, chunks, vectors, EVAL_LEVEL, top_n=20)
    cands = [(s, c) for s, c, _v, _b in fused]
    return [c for _rr, _f, c in rerank(q, cands, top_n=DEPTH)]


RETRIEVERS = {
    "vector": vector_only,
    "bm25": bm25_only,
    "hybrid": hybrid_only,
    "vector+rerank": vector_rerank,
    "hybrid+rerank": hybrid_rerank,
}
SHORT = {"vector": "vec", "bm25": "bm25", "hybrid": "hyb", "vector+rerank": "vec+rr", "hybrid+rerank": "hyb+rr"}


def first_correct_rank(results, expected):
    labels = [label(c) for c in results]
    ranks = [labels.index(e) + 1 for e in expected if e in labels]
    return min(ranks) if ranks else None


def run_all():
    table = {}
    for name, fn in RETRIEVERS.items():
        fn(QUESTIONS[0]["q"])  # warm-up: model loading is not retrieval cost
        ranks, times = [], []
        for item in QUESTIONS:
            t0 = time.perf_counter()
            results = fn(item["q"])
            times.append((time.perf_counter() - t0) * 1000)
            ranks.append(first_correct_rank(results, item["expected"]))
        table[name] = {"ranks": ranks, "ms": sum(times) / len(times)}
    return table


def recip(ranks):
    return [1 / r if r else 0.0 for r in ranks]


def bootstrap_interval(diffs, n=2000, seed=0):
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(diffs, k=len(diffs))) / len(diffs) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


if __name__ == "__main__":
    table = run_all()
    total = len(QUESTIONS)

    print(f"\n{'retriever':15} {'hit@1':>6} {'hit@3':>6} {'MRR':>6} {'ms/query':>9}")
    for name, row in table.items():
        ranks = row["ranks"]
        hit1 = sum(r == 1 for r in ranks)
        hit3 = sum(r is not None and r <= 3 for r in ranks)
        mrr = sum(recip(ranks)) / total
        print(f"{name:15} {hit1:>3}/{total:<2} {hit3:>3}/{total:<2} {mrr:6.3f} {row['ms']:9.1f}")

    print("\nFirst correct rank per question ('-' = not in top 10)")
    print(f"{'type':11} " + " ".join(f"{SHORT[n]:>6}" for n in RETRIEVERS) + "  question")
    for i, item in enumerate(QUESTIONS):
        cells = " ".join(f"{(table[n]['ranks'][i] or '-'):>6}" for n in RETRIEVERS)
        print(f"{item['type']:11} {cells}  {item['q'][:50]}")

    print("\nhit@1 by question type")
    print(f"{'type':11} {'n':>3} " + " ".join(f"{SHORT[n]:>6}" for n in RETRIEVERS))
    for t in sorted({q["type"] for q in QUESTIONS}):
        idx = [i for i, q in enumerate(QUESTIONS) if q["type"] == t]
        cells = " ".join(f"{sum(table[n]['ranks'][i] == 1 for i in idx):>6}" for n in RETRIEVERS)
        print(f"{t:11} {len(idx):>3} {cells}")

    print("\nMRR difference vs vector (bootstrap, 95% interval)")
    base = recip(table["vector"]["ranks"])
    for name in RETRIEVERS:
        if name == "vector":
            continue
        diffs = [a - b for a, b in zip(recip(table[name]["ranks"]), base)]
        lo, hi = bootstrap_interval(diffs)
        verdict = "distinguishable" if lo > 0 or hi < 0 else "not distinguishable"
        print(f"{name:15} {sum(diffs) / len(diffs):+.3f}  [{lo:+.3f}, {hi:+.3f}]  {verdict}")