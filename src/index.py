import json
from pathlib import Path

import faiss
import numpy as np

import time

from embeddings import embed_text, embed_texts


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

PROVISIONS_FILE = DATA_DIR / "provisions.jsonl"
INDEX_FILE = DATA_DIR / "policy.index"
METADATA_FILE = DATA_DIR / "index_metadata.json"


def load_provisions():
    provisions = []

    with PROVISIONS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                provisions.append(json.loads(line))

    return provisions


def build_index(provisions, batch_size=20):
    vectors = []
    total = len(provisions)

    for i in range(0, total, batch_size):
        batch_provisions = provisions[i : i + batch_size]
        batch_texts = [p["text"] for p in batch_provisions]

        end_idx = min(i + batch_size, total)
        print(f"Embedding batch {i + 1}-{end_idx}/{total}...")

        batch_vectors = embed_texts(batch_texts)
        vectors.extend(batch_vectors)

        if end_idx < total:
            time.sleep(0.5)

    matrix = np.vstack(vectors).astype("float32")

    # Normalize vectors so inner product behaves like cosine similarity.
    faiss.normalize_L2(matrix)

    dimension = matrix.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(matrix)

    return index


def save_metadata(provisions):
    metadata = []

    for i, provision in enumerate(provisions):
        metadata.append(
            {
                "vector_id": i,
                "clause_id": provision["clause_id"],
                "source_doc": provision["source_doc"],
            }
        )

    with METADATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main():
    print("Loading provisions...")

    provisions = load_provisions()

    print(f"Loaded {len(provisions)} provisions.")

    print("\nBuilding FAISS index...")

    index = build_index(provisions)

    faiss.write_index(index, str(INDEX_FILE))

    save_metadata(provisions)

    print("\n===================================")
    print("FAISS index created successfully!")
    print(f"Vectors: {index.ntotal}")
    print(f"Dimension: {index.d}")
    print(f"Index: {INDEX_FILE}")
    print(f"Metadata: {METADATA_FILE}")
    print("===================================")


if __name__ == "__main__":
    main()