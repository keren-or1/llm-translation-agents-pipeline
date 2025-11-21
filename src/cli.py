#!/usr/bin/env python3
"""
CLI Module
Handles command-line argument parsing and configuration
"""

import argparse


def parse_arguments():
    """
    Parse command-line arguments for the translation experiment system.

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - input: Path to input JSON file (optional)
            - output: Path to output JSON file
            - graph_output: Path to output graph image
            - cache_dir: Directory for caching embeddings
            - clear_cache: Boolean flag to clear cache before running
    """
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

    parser.add_argument('--input', '-i', type=str, default=None,
                        help='Path to JSON file containing experiments (default: use hardcoded data)')
    parser.add_argument('--output', '-o', type=str, default='docs/experiment_results.json',
                        help='Path to output JSON file (default: docs/experiment_results.json)')
    parser.add_argument('--graph-output', '-g', type=str, default='screenshots/translation_distance_graph.png',
                        help='Path to output graph image (default: screenshots/translation_distance_graph.png)')
    parser.add_argument('--cache-dir', '-c', type=str, default='.cache',
                        help='Directory for caching embeddings (default: .cache)')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear cache before running')

    return parser.parse_args()
