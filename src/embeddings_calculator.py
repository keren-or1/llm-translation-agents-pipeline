#!/usr/bin/env python3
"""
Embeddings and Cosine Distance Calculator for Translation Agent Experiment
This script computes embeddings for original and final translated sentences,
then calculates cosine distance between them.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances
import json
from typing import Dict, List, Tuple

class EmbeddingsCalculator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embeddings calculator.

        Args:
            model_name: The sentence transformer model to use
        """
        print(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")

    def calculate_embeddings(self, sentences: List[str]) -> np.ndarray:
        """
        Calculate embeddings for a list of sentences.

        Args:
            sentences: List of sentences to embed

        Returns:
            numpy array of embeddings
        """
        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        return embeddings

    def calculate_cosine_distance(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine distance between two embeddings.
        Cosine distance = 1 - cosine_similarity

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine distance value
        """
        # Reshape for pairwise calculation
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)

        # Calculate cosine distance
        distance = cosine_distances(embedding1, embedding2)[0][0]
        return float(distance)

    def process_experiment(self, error_percentage: int, original_sentence: str, final_sentence: str) -> Dict:
        """
        Process a single experiment by calculating embeddings and distance.

        Args:
            error_percentage: The error percentage for this experiment
            original_sentence: The original English sentence
            final_sentence: The final English sentence after translation chain

        Returns:
            Dictionary with results
        """
        # Calculate embeddings
        embeddings = self.calculate_embeddings([original_sentence, final_sentence])
        original_embedding = embeddings[0]
        final_embedding = embeddings[1]

        # Calculate cosine distance
        distance = self.calculate_cosine_distance(original_embedding, final_embedding)

        # Calculate cosine similarity for reference
        similarity = 1 - distance

        result = {
            "error_percentage": error_percentage,
            "original_sentence": original_sentence,
            "final_sentence": final_sentence,
            "cosine_distance": distance,
            "cosine_similarity": similarity,
            "original_embedding_sample": original_embedding[:5].tolist(),  # First 5 dimensions for inspection
            "final_embedding_sample": final_embedding[:5].tolist()
        }

        return result

    def batch_process_experiments(self, experiments: List[Dict]) -> List[Dict]:
        """
        Process multiple experiments at once.

        Args:
            experiments: List of dicts with keys: error_percentage, original_sentence, final_sentence

        Returns:
            List of result dictionaries
        """
        results = []
        for exp in experiments:
            result = self.process_experiment(
                exp["error_percentage"],
                exp["original_sentence"],
                exp["final_sentence"]
            )
            results.append(result)
            print(f"✓ Processed {exp['error_percentage']}% error - Distance: {result['cosine_distance']:.4f}")

        return results


def main():
    """
    Main function to run embeddings calculations.
    This reads experiment results and outputs distance metrics.
    """
    # Initialize calculator
    calculator = EmbeddingsCalculator()

    # Experiment data - to be filled with actual translation results
    # This is a placeholder structure
    experiments = [
        {
            "error_percentage": 0,
            "original_sentence": "The advanced artificial intelligence system successfully translates complex linguistic patterns across multiple languages with remarkable accuracy and precision.",
            "final_sentence": "The advanced artificial intelligence system successfully translates complex linguistic models into multiple languages with exceptional accuracy and precision."
        }
        # Additional experiments will be added here
    ]

    print("\n" + "="*70)
    print("EMBEDDINGS AND VECTOR DISTANCE CALCULATION")
    print("="*70 + "\n")

    # Process experiments
    results = calculator.batch_process_experiments(experiments)

    # Display results
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)

    for result in results:
        print(f"\nError Percentage: {result['error_percentage']}%")
        print(f"  Original: {result['original_sentence'][:60]}...")
        print(f"  Final:    {result['final_sentence'][:60]}...")
        print(f"  Cosine Distance: {result['cosine_distance']:.6f}")
        print(f"  Cosine Similarity: {result['cosine_similarity']:.6f}")

    return results


if __name__ == "__main__":
    results = main()
