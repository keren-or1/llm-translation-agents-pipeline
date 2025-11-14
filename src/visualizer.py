#!/usr/bin/env python3
"""
Visualizer - Create graphs from experiment results

This script takes experiment results and generates visualizations showing
the relationship between error rate and vector distance.

Usage:
    python src/visualizer.py \
      --results results/analysis/experiment_results.json \
      --output results/graphs/
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict
import logging

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_results(filepath: str) -> pd.DataFrame:
    """Load results from JSON file into DataFrame."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    logger.info(f"Loaded {len(df)} result rows")
    return df


def create_main_graph(df: pd.DataFrame, output_dir: str) -> None:
    """
    Create main graph: Error Rate vs. Cosine Distance

    Args:
        df: Results DataFrame
        output_dir: Output directory
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Prepare data
    df = df.sort_values('error_rate')
    error_rates = df['error_rate'].astype(float).values
    distances = df['cosine_distance'].astype(float).values

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot line with markers
    ax.plot(
        error_rates,
        distances,
        marker='o',
        linestyle='-',
        linewidth=2.5,
        markersize=10,
        color='#2E86AB',
        markerfacecolor='#A23B72',
        markeredgewidth=2,
        markeredgecolor='#2E86AB',
        label='Cosine Distance',
        zorder=3
    )

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax.set_axisbelow(True)

    # Formatting
    ax.set_xlabel('Spelling Error Rate (%)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Cosine Distance', fontsize=13, fontweight='bold')
    ax.set_title(
        'Impact of Spelling Errors on Translation Quality\nOriginal vs. Final Translation Semantic Distance',
        fontsize=14,
        fontweight='bold',
        pad=20
    )

    # Set axis limits with some padding
    ax.set_ylim(-0.05, min(1.0, max(distances) + 0.15))
    ax.set_xlim(-5, max(error_rates) + 5)

    # Format x-axis as percentages
    ax.set_xticks(error_rates)
    ax.set_xticklabels([f"{int(x)}%" for x in error_rates])

    # Add value labels on points
    for x, y in zip(error_rates, distances):
        ax.annotate(
            f'{y:.4f}',
            xy=(x, y),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            fontsize=9,
            fontweight='bold'
        )

    # Legend
    ax.legend(loc='upper left', fontsize=11, framealpha=0.95)

    # Save figure
    output_path = Path(output_dir) / 'error_vs_distance.png'
    fig.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Saved graph to {output_path}")

    # Also save as SVG for vector format
    svg_path = Path(output_dir) / 'error_vs_distance.svg'
    plt.savefig(svg_path, format='svg', bbox_inches='tight')
    logger.info(f"Saved SVG to {svg_path}")

    plt.close()


def create_detailed_analysis_graph(df: pd.DataFrame, output_dir: str) -> None:
    """
    Create detailed analysis with multiple subplots.

    Args:
        df: Results DataFrame
        output_dir: Output directory
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df = df.sort_values('error_rate')

    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(
        'Detailed Analysis: Error Propagation Through Translation Chain',
        fontsize=16,
        fontweight='bold',
        y=0.995
    )

    # 1. Error Rate vs. Cosine Distance (main)
    ax1 = axes[0, 0]
    error_rates = df['error_rate'].astype(float).values
    distances = df['cosine_distance'].astype(float).values

    ax1.plot(
        error_rates,
        distances,
        marker='o',
        linestyle='-',
        linewidth=2,
        markersize=8,
        color='#2E86AB',
        markerfacecolor='#A23B72'
    )
    ax1.fill_between(error_rates, distances, alpha=0.2, color='#A23B72')
    ax1.set_xlabel('Error Rate (%)', fontweight='bold')
    ax1.set_ylabel('Cosine Distance', fontweight='bold')
    ax1.set_title('Cosine Distance vs. Error Rate')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(error_rates)

    # 2. Error Rate vs. Similarity (inverse)
    ax2 = axes[0, 1]
    similarities = df['cosine_similarity'].astype(float).values

    ax2.plot(
        error_rates,
        similarities,
        marker='s',
        linestyle='-',
        linewidth=2,
        markersize=8,
        color='#F18F01',
        markerfacecolor='#FFBC35'
    )
    ax2.fill_between(error_rates, similarities, alpha=0.2, color='#FFBC35')
    ax2.set_xlabel('Error Rate (%)', fontweight='bold')
    ax2.set_ylabel('Cosine Similarity', fontweight='bold')
    ax2.set_title('Cosine Similarity vs. Error Rate')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.05)
    ax2.set_xticks(error_rates)

    # 3. Distance degradation rate
    ax3 = axes[1, 0]
    degradation = np.diff(distances, prepend=[0])

    colors = ['#06A77D' if d <= 0 else '#D62839' for d in degradation]
    ax3.bar(error_rates, degradation, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('Error Rate (%)', fontweight='bold')
    ax3.set_ylabel('Distance Increase', fontweight='bold')
    ax3.set_title('Marginal Degradation per 10% Error Increase')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_xticks(error_rates)
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

    # 4. Summary statistics table
    ax4 = axes[1, 1]
    ax4.axis('off')

    # Calculate statistics
    stats = {
        'Min Distance': f"{distances.min():.4f}",
        'Max Distance': f"{distances.max():.4f}",
        'Mean Distance': f"{distances.mean():.4f}",
        'Std Deviation': f"{distances.std():.4f}",
        'Total Increase': f"{distances[-1] - distances[0]:.4f}",
        'Data Points': str(len(df))
    }

    # Create table
    table_data = [[k, v] for k, v in stats.items()]
    table = ax4.table(
        cellText=table_data,
        colLabels=['Metric', 'Value'],
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)

    # Style header
    for i in range(2):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F0F0F0')
            else:
                table[(i, j)].set_facecolor('#FFFFFF')

    # Save figure
    output_path = Path(output_dir) / 'detailed_analysis.png'
    fig.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Saved detailed analysis to {output_path}")

    plt.close()


def create_comparison_table(df: pd.DataFrame, output_dir: str) -> None:
    """
    Create a comparison table visualization.

    Args:
        df: Results DataFrame
        output_dir: Output directory
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df = df.sort_values('error_rate')

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')

    # Prepare table data
    table_data = []
    for idx, row in df.iterrows():
        error_rate = int(row['error_rate'])
        similarity = float(row['cosine_similarity'])
        distance = float(row['cosine_distance'])

        table_data.append([
            f"{error_rate}%",
            f"{similarity:.4f}",
            f"{distance:.4f}",
            row['original_sentence'][:40] + "..." if len(str(row['original_sentence'])) > 40 else row['original_sentence'],
            row['final_sentence'][:40] + "..." if len(str(row['final_sentence'])) > 40 else row['final_sentence'],
        ])

    # Create table
    table = ax.table(
        cellText=table_data,
        colLabels=['Error Rate', 'Similarity', 'Distance', 'Original (excerpt)', 'Final (excerpt)'],
        cellLoc='left',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Style header
    for i in range(5):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Alternate row colors and color-code distance
    for i in range(1, len(table_data) + 1):
        distance = float(table_data[i-1][2])
        bg_color = '#FFFFFF' if i % 2 == 0 else '#F5F5F5'

        for j in range(5):
            cell = table[(i, j)]
            cell.set_facecolor(bg_color)

            # Highlight distance column with color gradient
            if j == 2:
                if distance < 0.2:
                    cell.set_facecolor('#C8E6C9')
                elif distance < 0.4:
                    cell.set_facecolor('#FFF9C4')
                elif distance < 0.6:
                    cell.set_facecolor('#FFE0B2')
                else:
                    cell.set_facecolor('#FFCDD2')

    # Save figure
    output_path = Path(output_dir) / 'comparison_table.png'
    fig.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Saved comparison table to {output_path}")

    plt.close()


def generate_all_visualizations(results_file: str, output_dir: str) -> None:
    """Generate all visualizations."""
    df = load_results(results_file)

    logger.info("Generating main graph...")
    create_main_graph(df, output_dir)

    logger.info("Generating detailed analysis...")
    create_detailed_analysis_graph(df, output_dir)

    logger.info("Generating comparison table...")
    create_comparison_table(df, output_dir)

    logger.info("All visualizations complete!")


def main():
    parser = argparse.ArgumentParser(
        description='Create visualizations from experiment results'
    )
    parser.add_argument(
        '--results',
        required=True,
        help='JSON file with experiment results'
    )
    parser.add_argument(
        '--output',
        default='results/graphs/',
        help='Output directory for graphs'
    )
    parser.add_argument(
        '--graph-type',
        choices=['main', 'detailed', 'table', 'all'],
        default='all',
        help='Type of graph to create'
    )

    args = parser.parse_args()

    df = load_results(args.results)

    if args.graph_type in ['main', 'all']:
        create_main_graph(df, args.output)

    if args.graph_type in ['detailed', 'all']:
        create_detailed_analysis_graph(df, args.output)

    if args.graph_type in ['table', 'all']:
        create_comparison_table(df, args.output)

    logger.info("Visualization complete!")


if __name__ == '__main__':
    main()
