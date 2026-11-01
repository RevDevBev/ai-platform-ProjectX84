from reranker import rerank
from search import load_index, search

ANSWERABLE = [
    "What happens to a message that fails three times?",
    "How do I replay messages from the dead-letter queue?",
    "How are duplicate messages prevented?",
    "How often are the CI keys rotated?",
    "Can I push straight to the main branch?",
    "How do I find out why messages are in the dead-letter queue?",
]

UNANSWERABLE = [
    "What is the capital of France?",
    "How do I bake sourdough bread?",
    "What is the company holiday policy?",
    "Who is the CEO of the company?",
    "What is the maximum message size SQS allows?",
]

chunks, vectors = load_index()


def top_scores(question):
    first = search(question, chunks, vectors, k=min(20, len(chunks)))
    ranked = rerank(question, first, top_n=1)
    return ranked[0][0], first[0][0]


def run(label, questions):
    print(f"\n{label}")
    scores = []
    for q in questions:
        rr, cos = top_scores(q)
        scores.append(rr)
        print(f"  rerank {rr:7.2f}   cosine {cos:.3f}   {q}")
    return scores


ans = run("ANSWERABLE (the documents contain the answer)", ANSWERABLE)
un = run("UNANSWERABLE (the documents do not contain the answer)", UNANSWERABLE)

print(f"\nlowest answerable rerank score    : {min(ans):.2f}")
print(f"highest unanswerable rerank score : {max(un):.2f}")
if min(ans) > max(un):
    print(f"clean gap: a threshold near {(min(ans) + max(un)) / 2:.2f} separates them")
else:
    print("overlap: no single threshold separates every case (see notes)")