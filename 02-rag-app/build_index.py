import json
from pathlib import Path

import numpy as np

from embedder import MODEL_NAME, embed_passages

HERE = Path(__file__).parent

chunks = json.loads((HERE / "chunks.json").read_text(encoding="utf-8"))
vectors = embed_passages([c["text"] for c in chunks])
np.savez(HERE / "index.npz", vectors=vectors, model=MODEL_NAME)
print(f"embedded {len(chunks)} chunks, vector size {vectors.shape[1]}")