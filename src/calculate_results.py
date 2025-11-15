#!/usr/bin/env python3
"""
Complete Translation Agent Experiment Results Calculator
Calculates embeddings, cosine distances, creates tables and visualizations

Features:
- Load experiments from JSON input file
- CLI argument support: --input <file> --output <file> --cache-dir <dir>
- Automatic caching of intermediate embeddings
- Backward compatible with hardcoded defaults
"""

import numpy as np
import json
import argparse
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import pandas as pd

class ExperimentResultsCalculator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = ".cache"):
        """Initialize the calculator with sentence embeddings model."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        print("✓ Model loaded successfully\n")

    def get_embedding_cache_path(self, text: str) -> Path:
        """Get cache file path for a given text."""
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.cache_dir / f"embedding_{text_hash}.npy"

    def get_or_calculate_embedding(self, text: str) -> np.ndarray:
        """Get embedding from cache or calculate and cache it."""
        cache_path = self.get_embedding_cache_path(text)

        if cache_path.exists():
            embedding = np.load(cache_path)
            return embedding

        embedding = self.model.encode(text, convert_to_numpy=True)
        np.save(cache_path, embedding)
        return embedding

    def calculate_cosine_distance(self, embedding1: np.ndarray, embedding2: np.ndarray) -> Tuple[float, float]:
        """
        Calculate cosine distance and similarity between embeddings.
        Returns: (distance, similarity)
        """
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)
        distance = cosine_distances(embedding1, embedding2)[0][0]
        similarity = 1 - distance
        return float(distance), float(similarity)

    def process_all_experiments(self, experiments: List[Dict]) -> List[Dict]:
        """Process all experiments and calculate distances."""
        results = []

        for exp in experiments:
            original = exp["original_english"]
            final = exp["final_english"]
            error_pct = exp["error_percentage"]

            # Get embeddings with caching
            original_emb = self.get_or_calculate_embedding(original)
            final_emb = self.get_or_calculate_embedding(final)

            # Calculate distances
            distance, similarity = self.calculate_cosine_distance(original_emb, final_emb)

            result = {
                "error_percentage": error_pct,
                "original_english": original,
                "final_english": final,
                "cosine_distance": distance,
                "cosine_similarity": similarity
            }
            results.append(result)
            print(f"✓ {error_pct:>2}% errors - Distance: {distance:.6f} | Similarity: {similarity:.6f}")

        return results

    def create_results_table(self, results: List[Dict]) -> pd.DataFrame:
        """Create a pandas DataFrame with results."""
        df = pd.DataFrame([
            {
                "Error %": r["error_percentage"],
                "Original English": r["original_english"][:50] + "...",
                "Final English": r["final_english"][:50] + "...",
                "Cosine Distance": f"{r['cosine_distance']:.6f}",
                "Cosine Similarity": f"{r['cosine_similarity']:.6f}"
            }
            for r in results
        ])
        return df

    def create_graph(self, results: List[Dict], output_path: str = "translation_distance_graph.png"):
        """Create a visualization of error percentage vs. cosine distance."""
        error_percentages = [r["error_percentage"] for r in results]
        distances = [r["cosine_distance"] for r in results]
        similarities = [r["cosine_similarity"] for r in results]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Plot 1: Cosine Distance vs Error Percentage
        ax1.plot(error_percentages, distances, marker='o', linewidth=2, markersize=8, color='#e74c3c')
        ax1.scatter(error_percentages, distances, s=100, color='#e74c3c', alpha=0.6, zorder=5)
        ax1.set_xlabel("Spelling Error Percentage (%)", fontsize=12, fontweight='bold')
        ax1.set_ylabel("Cosine Distance", fontsize=12, fontweight='bold')
        ax1.set_title("Translation Chain: Error Impact on Semantic Distance", fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(error_percentages)

        # Add value labels on points
        for x, y in zip(error_percentages, distances):
            ax1.annotate(f'{y:.4f}', xy=(x, y), xytext=(0, 10), textcoords='offset points',
                        ha='center', fontsize=9, fontweight='bold')

        # Plot 2: Cosine Similarity vs Error Percentage
        ax2.plot(error_percentages, similarities, marker='s', linewidth=2, markersize=8, color='#27ae60')
        ax2.scatter(error_percentages, similarities, s=100, color='#27ae60', alpha=0.6, zorder=5)
        ax2.set_xlabel("Spelling Error Percentage (%)", fontsize=12, fontweight='bold')
        ax2.set_ylabel("Cosine Similarity", fontsize=12, fontweight='bold')
        ax2.set_title("Translation Chain: Semantic Preservation", fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(error_percentages)
        ax2.set_ylim([min(similarities) - 0.01, 1.0])

        # Add value labels on points
        for x, y in zip(error_percentages, similarities):
            ax2.annotate(f'{y:.4f}', xy=(x, y), xytext=(0, 10), textcoords='offset points',
                        ha='center', fontsize=9, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Graph saved to: {output_path}")
        return fig


def get_default_experiments() -> List[Dict]:
    """Return default hardcoded experiments for backward compatibility."""
    return [
        {
            "error_percentage": 0,
            "original_english": "The advanced artificial intelligence system successfully translates complex linguistic patterns across multiple languages with remarkable accuracy and precision.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models into multiple languages with exceptional accuracy and precision."
        },
        {
            "error_percentage": 10,
            "original_english": "The advansed artificial inteligence system sucessfully translates complex linguistic patterns across multiple languages with remarkable accuracy and precision.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models into multiple languages with exceptional accuracy and precision."
        },
        {
            "error_percentage": 20,
            "original_english": "The advansed artificial inteligence sistem sucessfully translates complex lingustic patterns across multiple languages with remarkable accuracy and precision.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models into multiple languages with exceptional accuracy and precision."
        },
        {
            "error_percentage": 30,
            "original_english": "The advansed artificial inteligence sistem sucessfully translates complex lingustic patterns across multiple langages with remarkble accuracy and precision.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models in multiple languages with exceptional accuracy and precision."
        },
        {
            "error_percentage": 40,
            "original_english": "The advansed articial inteligence sistem sucessfully transltes complex lingustic patterns acros multiple langages with remarkble accuracy and presicion.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models across multiple languages with exceptional accuracy and reliability."
        },
        {
            "error_percentage": 50,
            "original_english": "The advansed articial inteligence sistem sucsessfully transltes complx lingustic patters acros multple langages with remarkble acuracy and presicion.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models between multiple languages with exceptional accuracy and reliability."
        }
    ]


def load_experiments(input_file: str) -> List[Dict]:
    """Load experiments from JSON file."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Support both direct list and wrapped format
        if isinstance(data, list):
            experiments = data
        elif isinstance(data, dict) and 'experiments' in data:
            experiments = data['experiments']
        else:
            print(f"Error: Input file must contain 'experiments' list")
            return None

        print(f"✓ Loaded {len(experiments)} experiments from {input_file}\n")
        return experiments
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{input_file}'")
        return None


def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Calculate embeddings and cosine distances for translation experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 calculate_results.py
  python3 calculate_results.py --input docs/experiments_input.json
  python3 calculate_results.py --input experiments.json --output results.json --cache-dir .embeddings_cache
        """
    )

    parser.add_argument(
        '--input', '-i',
        type=str,
        default=None,
        help='Path to JSON file containing experiments (default: use hardcoded data)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default='docs/experiment_results.json',
        help='Path to output JSON file (default: docs/experiment_results.json)'
    )

    parser.add_argument(
        '--graph-output', '-g',
        type=str,
        default='screenshots/translation_distance_graph.png',
        help='Path to output graph image (default: screenshots/translation_distance_graph.png)'
    )

    parser.add_argument(
        '--cache-dir', '-c',
        type=str,
        default='.cache',
        help='Directory for caching embeddings (default: .cache)'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear cache before running'
    )

    args = parser.parse_args()

    # Clear cache if requested
    if args.clear_cache:
        import shutil
        cache_path = Path(args.cache_dir)
        if cache_path.exists():
            shutil.rmtree(cache_path)
            print(f"✓ Cleared cache directory: {args.cache_dir}\n")

    print("="*80)
    print("TRANSLATION AGENT EXPERIMENT: EMBEDDINGS AND VECTOR DISTANCE ANALYSIS")
    print("="*80)
    print()

    # Load experiments
    if args.input:
        experiments = load_experiments(args.input)
        if experiments is None:
            print("Falling back to default hardcoded experiments...")
            experiments = get_default_experiments()
    else:
        print("Using default hardcoded experiments")
        experiments = get_default_experiments()

    print()

    # Create output directories if needed
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.graph_output).parent.mkdir(parents=True, exist_ok=True)

    # Initialize calculator
    calculator = ExperimentResultsCalculator(cache_dir=args.cache_dir)

    # Process all experiments
    print("Processing experiments...")
    print("-" * 80)
    results = calculator.process_all_experiments(experiments)

    # Create results table
    print("\n" + "="*80)
    print("RESULTS TABLE")
    print("="*80)
    df = calculator.create_results_table(results)
    print(df.to_string(index=False))

    # Create detailed results summary
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)
    for r in results:
        print(f"\nError Percentage: {r['error_percentage']}%")
        print(f"  Original: {r['original_english']}")
        print(f"  Final:    {r['final_english']}")
        print(f"  Cosine Distance:  {r['cosine_distance']:.6f}")
        print(f"  Cosine Similarity: {r['cosine_similarity']:.6f}")

    # Save results to JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Results saved to: {args.output}")

    # Create visualization
    print("\nGenerating graph...")
    print("-" * 80)
    calculator.create_graph(results, args.graph_output)

    # Statistical analysis
    print("\n" + "="*80)
    print("STATISTICAL ANALYSIS")
    print("="*80)
    distances = [r["cosine_distance"] for r in results]
    print(f"Minimum distance:  {min(distances):.6f} (at {results[distances.index(min(distances))]['error_percentage']}% errors)")
    print(f"Maximum distance:  {max(distances):.6f} (at {results[distances.index(max(distances))]['error_percentage']}% errors)")
    print(f"Average distance:  {np.mean(distances):.6f}")
    print(f"Std deviation:     {np.std(distances):.6f}")

    # Distance change analysis
    print("\nDistance Change Analysis:")
    for i in range(1, len(results)):
        prev_dist = results[i-1]["cosine_distance"]
        curr_dist = results[i]["cosine_distance"]
        change = curr_dist - prev_dist
        pct_change = (change / prev_dist * 100) if prev_dist > 0 else 0
        print(f"  {results[i-1]['error_percentage']}% → {results[i]['error_percentage']}%: "
              f"{change:+.6f} ({pct_change:+.2f}%)")

    # Cache info
    cache_size = sum(f.stat().st_size for f in Path(args.cache_dir).glob('**/*') if f.is_file()) / 1024
    print(f"\n✓ Embedding cache size: {cache_size:.2f} KB")
    print(f"✓ Cache directory: {args.cache_dir}")

    print("\n" + "="*80)
    print("✓ EXPERIMENT COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
