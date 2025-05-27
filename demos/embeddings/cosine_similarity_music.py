#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
import openai

GENRES = [
    "Classical",
    "Hip Hop",
    "Jazz",
    "Pop",
    "Rock",
    "Electronic",
    "Blues",
    "Country",
    "Reggae",
    "R&B",
]
EMBEDDING_MODEL = "text-embedding-3-small"  # fast & inexpensive
CACHE_FILE = Path("genre_embeddings.json")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def embed(text: str) -> np.ndarray:
    """Get a fresh embedding vector for a piece of text."""
    response = openai.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return np.array(response.data[0].embedding, dtype=np.float32)


def load_cache() -> Dict[str, List[float]]:
    if CACHE_FILE.exists():
        with CACHE_FILE.open() as f:
            return json.load(f)
    return {}


def save_cache(cache: Dict[str, List[float]]) -> None:
    with CACHE_FILE.open("w") as f:
        json.dump(cache, f)


def np_cache_to_dict(cache_np: Dict[str, np.ndarray]) -> Dict[str, List[float]]:
    """Convert {str: np.ndarray} → {str: list} for JSON."""
    return {k: v.tolist() for k, v in cache_np.items()}


def dict_cache_to_np(cache_dict: Dict[str, List[float]]) -> Dict[str, np.ndarray]:
    """Convert {str: list} → {str: np.ndarray} after JSON load."""
    return {k: np.array(v, dtype=np.float32) for k, v in cache_dict.items()}


def configure_api_key() -> None:
    parser = argparse.ArgumentParser(
        description="Map user music preference to genre with cached embeddings"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)",
    )
    args = parser.parse_args()

    openai.api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        sys.exit("❌  Provide an API key via --api-key or environment variable.")


def build_embeddings() -> Dict[str, np.ndarray]:
    """Load cached embeddings, add any missing ones, and persist."""
    cache_dict = load_cache()
    cache_np = dict_cache_to_np(cache_dict)

    missing_genres = [g for g in GENRES if g not in cache_np]
    if missing_genres:
        print(f"📀  Caching {len(missing_genres)} new genres…")
        for genre in missing_genres:
            cache_np[genre] = embed(genre)
        # Persist the expanded cache
        save_cache(np_cache_to_dict(cache_np))
    return cache_np


def main() -> None:
    configure_api_key()
    genre_embeddings = build_embeddings()
    print(f"✅  Ready! Cached {len(genre_embeddings)} genre embeddings.")
    print("   Ask me what music you like (Ctrl-C to quit).\n")

    try:
        while True:
            user_input = input("🎵 You: ").strip()
            if not user_input:
                continue
            query_vec = embed(user_input)

            similarities = {
                genre: cosine_similarity(query_vec, vec)
                for genre, vec in genre_embeddings.items()
            }
            best_genre = max(similarities, key=similarities.get)
            print(f"🤖 Sounds like **{best_genre}**.\n")
    except KeyboardInterrupt:
        print("\n👋 Bye!")


if __name__ == "__main__":
    main()