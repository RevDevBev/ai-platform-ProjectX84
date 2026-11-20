import json
from pathlib import Path

from access import LEVELS, chunk_rank, user_rank
from hybrid_search import hybrid
from search import load_index, search

HERE = Path(__file__).parent
QUESTIONS = json.loads((HERE / "eval" / "questions.json").read_text(encoding="utf-8"))
chunks, vectors = load_index()

by_label = {}
for c in chunks:
    by_label.setdefault(f"{c['source']} > {c['section']}", []).append(c)


def answerable(item, level):
    return any(
        chunk_rank(c) <= user_rank(level)
        for label in item["expected"]
        for c in by_label.get(label, [])
    )


total_leaks = 0
print(f"{'level':11} answerable   leaks")
for level in LEVELS:
    ok = sum(answerable(item, level) for item in QUESTIONS)
    leaks = 0
    for item in QUESTIONS:
        results = [c for _s, c in search(item["q"], chunks, vectors, k=10, user_level=level)]
        results += [c for _s, c, _v, _b in hybrid(item["q"], chunks, vectors, level, top_n=10)]
        for c in results:
            if chunk_rank(c) > user_rank(level):
                leaks += 1
                print(f"LEAK at {level}: {c['id']} for: {item['q']}")
    total_leaks += leaks
    print(f"{level:11} {ok}/{len(QUESTIONS)}          {leaks}")

print("total leaks:", total_leaks)
raise SystemExit(1 if total_leaks else 0)