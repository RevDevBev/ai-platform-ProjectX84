import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from config import CANDIDATES, REFUSAL_TEXT, REFUSAL_THRESHOLD, TOP_N
from generator import BACKEND, generate
from reranker import rerank
from search import load_index, search

CITATION = re.compile(r"\[([\w\-]+#\d+)\]")
LOG_FILE = Path(__file__).parent / "logs" / "queries.jsonl"


def log_event(event):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def ask(question):
    started = time.perf_counter()
    chunks, vectors = load_index()
    candidates = search(question, chunks, vectors, k=min(CANDIDATES, len(chunks)))
    ranked = rerank(question, candidates, top_n=TOP_N)  # (rerank, first_stage, chunk)
    top_score = ranked[0][0] if ranked else None

    if top_score is None or top_score < REFUSAL_THRESHOLD:
        decision = "refused_low_relevance"
        answer = REFUSAL_TEXT
    else:
        hits = [(rr, chunk) for rr, _first, chunk in ranked]
        answer = generate(question, hits)
        decision = "refused_by_model" if REFUSAL_TEXT in answer else "answered"

    retrieved_ids = {chunk["id"] for _rr, _first, chunk in ranked}
    cited = set(CITATION.findall(answer))
    result = {
        "answer": answer,
        "decision": decision,
        "ranked": ranked,
        "cited": sorted(cited),
        "bad_citations": sorted(cited - retrieved_ids),
        "uncited": decision == "answered" and not cited and BACKEND == "bedrock",
        "top_score": top_score,
    }

    log_event(
        {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "question": question,
            "decision": decision,
            "generator": BACKEND,
            "threshold": REFUSAL_THRESHOLD,
            "retrieved": [
                {
                    "id": chunk["id"],
                    "access": chunk["access"],
                    "first_stage": round(first, 4),
                    "rerank": round(rr, 3),
                }
                for rr, first, chunk in ranked
            ],
            "cited": result["cited"],
            "bad_citations": result["bad_citations"],
            "answer": answer,
            "latency_ms": round((time.perf_counter() - started) * 1000),
        }
    )
    return result


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What happens to a message that fails three times?"
    result = ask(question)

    print(f"\nDECISION: {result['decision']}")
    print("ANSWER:\n" + result["answer"])
    print("\nRETRIEVED:", ", ".join(f"{c['id']} ({rr:.2f})" for rr, _f, c in result["ranked"]))
    if result["bad_citations"]:
        print("WARNING: cited ids that were not retrieved:", result["bad_citations"])
    if result["uncited"]:
        print("NOTE: the answer has no citations")