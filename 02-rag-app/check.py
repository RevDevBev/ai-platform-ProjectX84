from reranker import rerank
from search import load_index, search

CASES = [
    ("What happens to a message that fails three times?", "architecture-overview#01"),
    ("How do I replay messages from the dead-letter queue?", "runbook-dlq#02"),
    ("How are duplicate messages prevented?", "architecture-overview#02"),
    ("How often are the CI keys rotated?", "access-and-security#00"),
    ("Can I push straight to the main branch?", "access-and-security#01"),
    ("How do I find out why messages are in the dead-letter queue?", "runbook-dlq#01"),
]

chunks, vectors = load_index()
before1 = after1 = before3 = after3 = 0
for question, expected in CASES:
    first = search(question, chunks, vectors, k=min(20, len(chunks)))
    ids_before = [c["id"] for _, c in first[:3]]
    ids_after = [c["id"] for _, _, c in rerank(question, first, top_n=3)]
    before1 += ids_before[0] == expected
    after1 += ids_after[0] == expected
    before3 += expected in ids_before
    after3 += expected in ids_after
    print(question, "\n   before:", ids_before, "\n   after: ", ids_after)

n = len(CASES)
print(f"\nhit@1  before {before1}/{n}  after {after1}/{n}")
print(f"hit@3  before {before3}/{n}  after {after3}/{n}")