import re
import sys

from generator import generate
from search import load_index, search

CITATION = re.compile(r"\[([\w\-]+#\d+)\]")


def ask(question, k=3):
    chunks, vectors = load_index()
    hits = search(question, chunks, vectors, k=k)
    answer = generate(question, hits)

    retrieved = {c["id"]: c for _score, c in hits}
    cited = set(CITATION.findall(answer))
    return {
        "answer": answer,
        "hits": hits,
        "cited": sorted(cited),
        "bad_citations": sorted(cited - set(retrieved)),
        "sources": [
            f'{retrieved[i]["source"]} > {retrieved[i]["section"]}'
            for i in sorted(cited)
            if i in retrieved
        ],
    }


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What happens to a message that fails three times?"
    result = ask(question)

    print("\nANSWER:\n" + result["answer"])
    print("\nRETRIEVED:", ", ".join(f'{c["id"]} ({s:.2f})' for s, c in result["hits"]))
    if result["sources"]:
        print("SOURCES:", "; ".join(result["sources"]))
    if result["bad_citations"]:
        print("WARNING: cited ids that were not retrieved:", result["bad_citations"])
    if not result["cited"]:
        print("NOTE: the answer has no citations")