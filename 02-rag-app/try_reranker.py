from reranker import _encoder

question = "Can I redrive messages before fixing the cause?"
passages = [
    "Never redrive before the fix, because the messages will fail again.",
    "Redrive the messages as soon as possible, before the fix.",
    "The conditional put skips duplicates.",
]

for text, score in zip(passages, _encoder().rerank(question, passages)):
    print(f"{score:7.2f}  {text}")