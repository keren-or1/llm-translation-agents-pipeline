#!/usr/bin/env python3
"""
Embedding Calculator Module
Handles sentence embedding computation and caching operations
"""

import numpy as np
import hashlib
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances
from typing import Tuple


class EmbeddingCalculator:
    """
    Calculates and caches sentence embeddings for translation experiments.

    This class manages the computation of semantic embeddings using SentenceTransformer
    models, with built-in caching to improve performance on repeated calculations.

    Attributes:
        model (SentenceTransformer): The sentence embedding model
        cache_dir (Path): Directory path for storing cached embeddings
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = ".cache"):
        """
        Initialize the embedding calculator with specified model and cache directory.

        Args:
            model_name (str): Name of the SentenceTransformer model to use
            cache_dir (str): Directory path for caching computed embeddings
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        print("✓ Model loaded successfully\n")

    def get_embedding_cache_path(self, text: str) -> Path:
        """
        Generate cache file path for a given text using MD5 hash.

        Args:
            text (str): Input text to generate cache path for

        Returns:
            Path: Path object pointing to the cache file location
        """
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.cache_dir / f"embedding_{text_hash}.npy"

    def get_or_calculate_embedding(self, text: str) -> np.ndarray:
        """
        Retrieve embedding from cache or calculate and cache it.

        This method implements a cache-first strategy: if an embedding exists
        in the cache, it's loaded; otherwise, it's computed and saved.

        Args:
            text (str): Input text to embed

        Returns:
            np.ndarray: Embedding vector for the input text
        """
        cache_path = self.get_embedding_cache_path(text)

        if cache_path.exists():
            embedding = np.load(cache_path)
            return embedding

        embedding = self.model.encode(text, convert_to_numpy=True)
        np.save(cache_path, embedding)
        return embedding

    def calculate_cosine_distance(self, embedding1: np.ndarray, embedding2: np.ndarray) -> Tuple[float, float]:
        """
        Calculate cosine distance and similarity between two embeddings.

        Cosine distance measures the angular difference between vectors,
        while cosine similarity measures their directional alignment.

        Args:
            embedding1 (np.ndarray): First embedding vector
            embedding2 (np.ndarray): Second embedding vector

        Returns:
            Tuple[float, float]: (cosine_distance, cosine_similarity)
                - cosine_distance: Range [0, 2], where 0 = identical
                - cosine_similarity: Range [-1, 1], where 1 = identical
        """
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)
        distance = cosine_distances(embedding1, embedding2)[0][0]
        similarity = 1 - distance
        return float(distance), float(similarity)
