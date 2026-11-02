import json
from pathlib import Path

from reranker import rerank
from search import load_index, search

HERE = Path(__file__).parent
QUESTIONS = json.loads((HERE / "eval" / "questions.json").read_text(encoding="utf-8"))

chunks, vectors = load_index()


def label(chunk):
    return f"{chunk['source']} > {chunk['section']}"


def vector_only(question, k=10):
    return [c for _s, c in search(question, chunks, vectors, k=k)]


def vector_rerank(question, k=10):
    candidates = search(question, chunks, vectors, k=min(20, len(chunks)))
    return [c for _rr, _f, c in rerank(question, candidates, top_n=k)]


RETRIEVERS = {"vector": vector_only, "vector+rerank": vector_rerank}


def evaluate(name, fn, verbose=True):
    hit1 = hit3 = 0
    rr_sum = 0.0
    for item in QUESTIONS:
        labels = [label(c) for c in fn(item["q"])]
        ranks = [labels.index(e) + 1 for e in item["expected"] if e in labels]
        best = min(ranks) if ranks else None
        hit1 += best == 1
        hit3 += best is not None and best <= 3
        rr_sum += 1 / best if best else 0
        if verbose and (best is None or best > 1):
            print(f"  [{name}] first correct rank = {best}:  {item['q']}")
    n = len(QUESTIONS)
    print(f"{name:15} hit@1 {hit1}/{n}   hit@3 {hit3}/{n}   MRR {rr_sum / n:.3f}\n")


if __name__ == "__main__":
    for name, fn in RETRIEVERS.items():
        evaluate(name, fn)