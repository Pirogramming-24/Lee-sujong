import numpy as np
from .embedding import embed_texts
from .index import load_index

def retrieve_movies(query: str, k: int = 5):
    index, metas = load_index()

    q_vec = embed_texts([query])[0]
    Q = np.array([q_vec], dtype="float32")

    D, I = index.search(Q, k)

    results = []
    for idx in I[0]:
        if 0 <= idx < len(metas):
            results.append(metas[idx])
    return results
