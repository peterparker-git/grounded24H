import json
from pathlib import Path

import faiss
import numpy as np

from embeddings import embed_query


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

INDEX_FILE = DATA_DIR / "policy.index"
PROVISIONS_FILE = DATA_DIR / "provisions.jsonl"


def load_index():
    """Load the FAISS policy index."""
    return faiss.read_index(str(INDEX_FILE))


def load_provisions():
    """Load policy provisions from JSONL."""
    provisions = []

    with PROVISIONS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                provisions.append(json.loads(line))

    return provisions


def retrieve(question: str, top_k: int = 5):
    """
    Retrieve the most relevant policy provisions
    for a user question.
    """

    index = load_index()
    provisions = load_provisions()

    query_vector = embed_query(question)

    query_vector = query_vector.reshape(1, -1).astype(np.float32)

    # Same normalization used when creating the FAISS index.
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(query_vector, top_k)

    results = []

    for score, vector_id in zip(scores[0], indices[0]):

        if vector_id < 0:
            continue

        provision = provisions[int(vector_id)]

        results.append({
            "vector_id": int(vector_id),
            "score": float(score),
            "clause_id": provision["clause_id"],
            "text": provision["text"],
            "source_doc": provision["source_doc"],
            "trigger": provision.get("trigger"),
            "effective_date": provision.get("effective_date"),
            "supersedes": provision.get("supersedes"),
            "retroactive": provision.get("retroactive", False),
            "apportionable": provision.get("apportionable", False),
            "superseded_value": provision.get("superseded_value"),
        })

    return results


def print_results(question, results):

    print()
    print("=" * 70)
    print("POLICY RETRIEVAL")
    print("=" * 70)

    print(f"\nQuestion:\n{question}")

    for i, result in enumerate(results, start=1):

        print()
        print(f"[{i}] §{result['clause_id']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {result['source_doc']}")
        print(f"Trigger: {result['trigger']}")
        print(f"Effective: {result['effective_date']}")
        print(f"Text: {result['text']}")

    print()
    print("=" * 70)


if __name__ == "__main__":

    question = input("Ask a policy question: ").strip()

    results = retrieve(question)

    print_results(question, results)