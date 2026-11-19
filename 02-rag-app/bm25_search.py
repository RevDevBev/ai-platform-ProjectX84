import math
import re
import sys
from collections import Counter

TOKEN = re.compile(r"[a-z0-9]+(?:[-_.][a-z0-9]+)*")
SPLIT = re.compile(r"[-_.]")
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "and", "or",
    "for", "on", "do", "does", "how", "what", "why", "i", "my", "we", "it", "be",
    "by", "at", "as", "this", "that", "with", "can", "me",
}


def tokenize(text):
    """Lowercase words. A token like err-4291 is kept whole AND split into parts."""
    tokens = []
    for tok in TOKEN.findall(text.lower()):
        if tok in STOPWORDS:
            continue
        tokens.append(tok)
        if SPLIT.search(tok):
            tokens.extend(p for p in SPLIT.split(tok) if p and p not in STOPWORDS)
    return tokens


class BM25:
    def __init__(self, docs_tokens, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs_tokens]
        self.lengths = [len(d) for d in docs_tokens]
        self.avg_len = sum(self.lengths) / len(self.lengths)
        df = Counter()
        for d in docs_tokens:
            df.update(set(d))
        n = len(docs_tokens)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query_tokens):
        out = []
        for tf, length in zip(self.tf, self.lengths):
            s = 0.0
            for t in query_tokens:
                f = tf.get(t, 0)
                if not f:
                    continue
                norm = f + self.k1 * (1 - self.b + self.b * length / self.avg_len)
                s += self.idf[t] * f * (self.k1 + 1) / norm
            out.append(s)
        return out


class BM25Index:
    def __init__(self, chunks):
        self.chunks = chunks
        self.bm25 = BM25([tokenize(c["text"]) for c in chunks])

    def search(self, query, k=3):
        scores = self.bm25.scores(tokenize(query))
        top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(scores[i], self.chunks[i]) for i in top]


if __name__ == "__main__":
    import json
    from pathlib import Path

    chunks = json.loads((Path(__file__).parent / "chunks.json").read_text(encoding="utf-8"))
    question = " ".join(sys.argv[1:]) or "What does ERR-4291 mean?"
    print("query tokens:", tokenize(question))
    for score, chunk in BM25Index(chunks).search(question):
        print(f"{score:6.2f}  {chunk['id']}  [{chunk['source']} > {chunk['section']}]")