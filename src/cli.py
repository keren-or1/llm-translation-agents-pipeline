#!/usr/bin/env python3
"""
CLI Module
Handles command-line argument parsing and configuration
"""

import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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

    # Get defaults from environment variables with fallbacks
    default_input = os.getenv('EXPERIMENTS_INPUT_FILE')
    default_output = os.getenv('RESULTS_OUTPUT_FILE', 'docs/experiment_results.json')
    default_graph = os.getenv('GRAPH_OUTPUT_FILE', 'screenshots/translation_distance_graph.png')
    default_cache = os.getenv('CACHE_DIR', '.cache')

    parser.add_argument('--input', '-i', type=str, default=default_input,
                        help=f'Path to JSON file containing experiments (default: {default_input or "use hardcoded data"})')
    parser.add_argument('--output', '-o', type=str, default=default_output,
                        help=f'Path to output JSON file (default: {default_output})')
    parser.add_argument('--graph-output', '-g', type=str, default=default_graph,
                        help=f'Path to output graph image (default: {default_graph})')
    parser.add_argument('--cache-dir', '-c', type=str, default=default_cache,
                        help=f'Directory for caching embeddings (default: {default_cache})')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear cache before running')

    return parser.parse_args()
