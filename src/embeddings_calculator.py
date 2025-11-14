#!/usr/bin/env python3
"""
Embeddings Calculator - Calculate embeddings and vector distances

This script calculates embeddings for sentences and computes cosine distances
between original and final translated sentences.

Usage:
    python src/embeddings_calculator.py \
      --original-sentence "The quick brown fox..." \
      --final-sentence "The fast brown fox..." \
      --model text-embedding-3-small
"""

import json
import argparse
import os
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from dotenv import load_dotenv

import numpy as np
from scipy.spatial.distance import cosine
from openai import OpenAI

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingsCalculator:
    """Calculate embeddings and measure semantic distance."""

    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize embeddings calculator.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Embedding model to use
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"Initialized with model: {model}")

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [e.embedding for e in embeddings]
        except Exception as e:
            logger.error(f"Error getting batch embeddings: {e}")
            raise

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Cosine similarity (0-1, higher = more similar)
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        # Normalize vectors
        vec1_norm = np.linalg.norm(vec1)
        vec2_norm = np.linalg.norm(vec2)

        if vec1_norm == 0 or vec2_norm == 0:
            return 0.0

        return float(np.dot(vec1, vec2) / (vec1_norm * vec2_norm))

    @staticmethod
    def cosine_distance(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine distance between two vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Cosine distance (0-2, lower = more similar)
        """
        similarity = EmbeddingsCalculator.cosine_similarity(vec1, vec2)
        return 1 - similarity

    def measure_distance(
        self,
        original_text: str,
        final_text: str
    ) -> Dict[str, float]:
        """
        Measure semantic distance between original and final text.

        Args:
            original_text: Original sentence
            final_text: Final translated sentence

        Returns:
            Dictionary with similarity and distance metrics
        """
        logger.info("Calculating embeddings...")

        # Get embeddings
        embeddings = self.get_embeddings_batch([original_text, final_text])
        original_embedding = embeddings[0]
        final_embedding = embeddings[1]

        # Calculate metrics
        similarity = self.cosine_similarity(original_embedding, final_embedding)
        distance = self.cosine_distance(original_embedding, final_embedding)

        logger.info(f"Cosine Similarity: {similarity:.4f}")
        logger.info(f"Cosine Distance: {distance:.4f}")

        return {
            'cosine_similarity': round(similarity, 6),
            'cosine_distance': round(distance, 6),
            'embedding_dimensions': len(original_embedding)
        }

    def analyze_translations(
        self,
        translations_file: str,
        output_dir: str = 'results/analysis/'
    ) -> None:
        """
        Analyze all translations from a file and output results.

        Args:
            translations_file: Path to JSON file with all translations
            output_dir: Output directory for results
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"Loading translations from {translations_file}")
        with open(translations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        results = []

        # Process each error rate
        for item in data:
            error_rate = item.get('error_rate', 'unknown')
            original = item.get('original_sentence', '')
            final = item.get('final_sentence', '')

            logger.info(f"Processing error rate: {error_rate}%")

            # Measure distance
            metrics = self.measure_distance(original, final)

            result = {
                'error_rate': error_rate,
                'original_sentence': original,
                'final_sentence': final,
                'cosine_similarity': metrics['cosine_similarity'],
                'cosine_distance': metrics['cosine_distance'],
                'tokens_used': item.get('tokens_used', 0)
            }
            results.append(result)

        # Save results
        output_file = Path(output_dir) / 'experiment_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved results to {output_file}")

        # Create summary CSV
        import pandas as pd
        df = pd.DataFrame(results)
        csv_file = Path(output_dir) / 'results_summary.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        logger.info(f"Saved summary to {csv_file}")

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Calculate embeddings and measure semantic distance'
    )
    parser.add_argument(
        '--original',
        help='Original sentence'
    )
    parser.add_argument(
        '--final',
        help='Final translated sentence'
    )
    parser.add_argument(
        '--translations',
        help='JSON file with all translations'
    )
    parser.add_argument(
        '--model',
        default='text-embedding-3-small',
        help='Embedding model to use'
    )
    parser.add_argument(
        '--output',
        default='results/analysis/',
        help='Output directory'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test mode'
    )
    parser.add_argument(
        '--api-key',
        help='OpenAI API key (defaults to OPENAI_API_KEY env var)'
    )

    args = parser.parse_args()

    # Initialize calculator
    try:
        calculator = EmbeddingsCalculator(
            api_key=args.api_key,
            model=args.model
        )
    except ValueError as e:
        logger.error(f"Initialization error: {e}")
        return

    # Test mode
    if args.test:
        logger.info("Running in test mode...")
        test_text = "The quick brown fox jumps over the lazy dog."
        embedding = calculator.get_embedding(test_text)
        logger.info(f"Test embedding dimension: {len(embedding)}")
        logger.info("Test mode successful!")
        return

    # Process single pair
    if args.original and args.final:
        logger.info("Measuring distance between two sentences...")
        metrics = calculator.measure_distance(args.original, args.final)
        print(json.dumps(metrics, indent=2))
        return

    # Process file
    if args.translations:
        logger.info("Analyzing translations from file...")
        results = calculator.analyze_translations(args.translations, args.output)
        logger.info(f"Analyzed {len(results)} translation pair(s)")
        return

    # No action specified
    logger.error("Please specify either --original/--final or --translations or --test")
    parser.print_help()


if __name__ == '__main__':
    main()
