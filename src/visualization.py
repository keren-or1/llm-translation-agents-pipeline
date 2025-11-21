#!/usr/bin/env python3
"""
Visualization Module
Handles creation of graphs and visual representations of results
"""

import matplotlib.pyplot as plt
from typing import List, Dict


def create_distance_graph(results: List[Dict], output_path: str = "translation_distance_graph.png"):
    """
    Create visualization of error percentage vs. cosine distance/similarity.

    This function generates a two-panel figure showing:
    - Left panel: Cosine Distance vs Error Percentage (shows semantic drift)
    - Right panel: Cosine Similarity vs Error Percentage (shows preservation)

    Args:
        results (List[Dict]): List of result dictionaries containing error_percentage,
                             cosine_distance, and cosine_similarity
        output_path (str): Path where the graph image will be saved

    Returns:
        matplotlib.figure.Figure: The generated figure object

    Note:
        Graph is saved as PNG with 300 DPI resolution for publication quality
    """
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
