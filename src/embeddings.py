import os
import time

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)


EMBEDDING_MODEL = "gemini-embedding-001"

def embed_texts(
    texts: list[str],
    task_type: str = "RETRIEVAL_DOCUMENT",
    max_retries: int = 5,
    initial_delay: float = 12.0,
) -> list[np.ndarray]:
    """
    Convert a list of text strings into Gemini embedding vectors in batch.
    Includes retry logic with exponential backoff for rate limit (429) errors.
    """
    if not texts:
        return []

    delay = initial_delay
    for attempt in range(max_retries):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type
                ),
            )
            return [
                np.array(emb.values, dtype=np.float32)
                for emb in response.embeddings
            ]
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < max_retries - 1:
                    print(f"\nRate limit reached (429). Waiting {delay:.1f}s before retrying (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(delay)
                    delay *= 1.5
                    continue
            raise


def embed_text(
    text: str,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> np.ndarray:
    """
    Convert text into a Gemini embedding vector.
    """

    return embed_texts(
        [text],
        task_type=task_type,
        max_retries=5,
        initial_delay=12.0,
    )[0]

def embed_query(text: str) -> np.ndarray:
    """
    Generate an embedding specifically for a search query.
    """

    return embed_text(
        text,
        task_type="RETRIEVAL_QUERY",
    )

if __name__ == "__main__":
    vector = embed_text(
        "A recipient must report a change of circumstances "
        "within 14 calendar days."
    )

    print("Embedding successful!")
    print("Dimensions:", len(vector))
    print("First 5 values:", vector[:5])