import json
from json import encoder
import sys
from pathlib import Path

import numpy as np

from embedder import embed_query, TextCrossEncoder

HERE = Path(__file__).parent


def load_index():
    chunks = json.loads((HERE / "chunks.json").read_text(encoding="utf-8"))
    vectors = np.load(HERE / "index.npz")["vectors"]
    return chunks, vectors


def search(query, chunks, vectors, k=3):
    scores = vectors @ embed_query(query)
    top = np.argsort(scores)[::-1][:k]
    return [(i, float(scores[i]), chunks[i]) for i in top]

def reranker(query, chunks):
    encoder = TextCrossEncoder(model_name="Xenova/ms-marco-MiniLM-L-6-v2")
    scores = list(encoder.rerank(query, chunks))
    top = np.argsort(scores)[::-1]
    return [(i) for i in top]
    
    
if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What happens to a message that fails three times?"
    chunks, vectors = load_index()
    unsorted_chunks = []
    unsorted_scores = []
    unsorted_ids = []
    for i,score, chunk in search(question, chunks, vectors):
        print(f"{score:.3f}  {chunk['id']}  [{chunk['section']}]  ({chunk['access']})")
        print("       " + chunk["text"].replace("\n", " ")[:110] + "...")
        unsorted_chunks.append(chunk["text"])
        unsorted_scores.append(score)
        unsorted_ids.append(i)

    print("\nReranking the top passages using a cross-encoder...\n")    

    for i in reranker(question, unsorted_chunks):
        print(f"{unsorted_scores[i]:.3f}  {chunks[unsorted_ids[i]]['id']}  [{chunks[unsorted_ids[i]]['section']}]  ({chunks[unsorted_ids[i]]['access']})")
        print("       " + chunks[unsorted_ids[i]]["text"].replace("\n", " ")[:110] + "...")
       