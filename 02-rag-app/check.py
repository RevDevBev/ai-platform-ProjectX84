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
hit1 = hit3 = 0
for question, expected in CASES:
    ids = [c["id"] for _, c in search(question, chunks, vectors, k=3)]
    hit1 += ids[0] == expected
    hit3 += expected in ids
    print(("OK  " if ids[0] == expected else "MISS"), question, "->", ids)
print(f"hit@1 {hit1}/{len(CASES)}   hit@3 {hit3}/{len(CASES)}")