#!/usr/bin/env python3
"""
Translation Agent Experiment Results Calculator
Main orchestration script for calculating embeddings, cosine distances, and generating visualizations

This script processes translation experiments through a three-agent pipeline and measures
semantic distance between original and final English outputs.
"""

import numpy as np
import json
import shutil
from pathlib import Path
from typing import List, Dict

from embedding_calculator import EmbeddingCalculator
from data_processor import get_default_experiments, load_experiments, create_results_table
from visualization import create_distance_graph
from statistics import print_statistical_analysis
from cli import parse_arguments


def process_experiments(calculator: EmbeddingCalculator, experiments: List[Dict]) -> List[Dict]:
    """
    Process all experiments and calculate embedding distances.

    Args:
        calculator (EmbeddingCalculator): Initialized embedding calculator instance
        experiments (List[Dict]): List of experiments with original and final English text

    Returns:
        List[Dict]: Results including cosine distance and similarity for each experiment
    """
    results = []

    for exp in experiments:
        original = exp["original_english"]
        final = exp["final_english"]
        error_pct = exp["error_percentage"]

        # Get embeddings with caching
        original_emb = calculator.get_or_calculate_embedding(original)
        final_emb = calculator.get_or_calculate_embedding(final)

        # Calculate distances
        distance, similarity = calculator.calculate_cosine_distance(original_emb, final_emb)

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


def main():
    """
    Main execution function orchestrating the entire experiment pipeline.

    Workflow:
    1. Parse command-line arguments
    2. Load or use default experiments
    3. Initialize embedding calculator
    4. Process experiments and calculate distances
    5. Generate visualization and save results
    6. Print statistical analysis
    """
    args = parse_arguments()

    # Clear cache if requested
    if args.clear_cache:
        cache_path = Path(args.cache_dir)
        if cache_path.exists():
            shutil.rmtree(cache_path)
            print(f"✓ Cleared cache directory: {args.cache_dir}\n")

    print("="*80)
    print("TRANSLATION AGENT EXPERIMENT: EMBEDDINGS AND VECTOR DISTANCE ANALYSIS")
    print("="*80)

    # Load experiments
    if args.input:
        experiments = load_experiments(args.input)
        if experiments is None:
            print("Falling back to default hardcoded experiments...")
            experiments = get_default_experiments()
    else:
        print("Using default hardcoded experiments")
        experiments = get_default_experiments()

    # Create output directories if needed
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.graph_output).parent.mkdir(parents=True, exist_ok=True)

    # Initialize calculator
    calculator = EmbeddingCalculator(cache_dir=args.cache_dir)

    # Process all experiments
    print("Processing experiments...")
    print("-" * 80)
    results = process_experiments(calculator, experiments)

    # Create results table
    print("\n" + "="*80)
    print("RESULTS TABLE")
    print("="*80)
    df = create_results_table(results)
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
    create_distance_graph(results, args.graph_output)

    # Statistical analysis and cache info
    print_statistical_analysis(results)
    cache_size = sum(f.stat().st_size for f in Path(args.cache_dir).glob('**/*') if f.is_file()) / 1024
    print(f"\n✓ Embedding cache size: {cache_size:.2f} KB")
    print(f"✓ Cache directory: {args.cache_dir}")

    print("\n" + "="*80)
    print("✓ EXPERIMENT COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
