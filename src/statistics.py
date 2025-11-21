#!/usr/bin/env python3
"""
Statistics Module
Handles statistical analysis and reporting of experiment results
"""

import numpy as np
from typing import List, Dict


def print_statistical_analysis(results: List[Dict]):
    """
    Print statistical analysis of experiment results.

    This function calculates and displays:
    - Min, max, mean, and standard deviation of cosine distances
    - Distance change analysis between consecutive error percentages
    - Percentage changes in semantic distance

    Args:
        results (List[Dict]): Processed experiment results containing
                             error_percentage and cosine_distance fields
    """
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
