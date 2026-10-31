import numpy as np
from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model = None


def _model_instance():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=MODEL_NAME)
    return _model


def _normalise(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, 1e-12, None)


def embed_passages(texts):
    vectors = np.array(list(_model_instance().embed(texts)), dtype="float32")
    return _normalise(vectors)


def embed_query(query):
    vector = np.array(
        list(_model_instance().embed([QUERY_PREFIX + query])), dtype="float32"
    )
    return _normalise(vector)[0]