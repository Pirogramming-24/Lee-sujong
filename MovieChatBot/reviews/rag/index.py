import os
import json
import numpy as np
import faiss

from .embedding import embed_texts

INDEX_DIR = "faiss_movies"
INDEX_FILE = os.path.join(INDEX_DIR, "index.faiss")
META_FILE = os.path.join(INDEX_DIR, "meta.json")

def save_index(texts: list[str], metadatas: list[dict]):
    os.makedirs(INDEX_DIR, exist_ok=True)

    vectors = embed_texts(texts)
    X = np.array(vectors, dtype="float32")

    dim = X.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(X)

    faiss.write_index(index, INDEX_FILE)

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadatas, f, ensure_ascii=False)

def load_index():
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "r", encoding="utf-8") as f:
        metas = json.load(f)
    return index, metas
