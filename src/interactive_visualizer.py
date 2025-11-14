#!/usr/bin/env python3
"""
Interactive Visualizer - Create interactive Plotly visualizations

This module creates professional, interactive visualizations using Plotly for
exploring error propagation through the translation chain. Outputs can be
viewed in browser (HTML) or exported as static images (PNG).

Usage:
    python src/interactive_visualizer.py \
      --results results/analysis/experiment_results.json \
      --output results/graphs/
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict
import logging

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InteractiveVisualizer:
    """
    Create interactive visualizations for translation experiment results.

    Features:
    - Interactive line/scatter plots with hover information
    - Dashboard-style multi-panel layouts
    - Exportable to HTML (interactive) and PNG (static)
    - Professional color schemes and styling
    - Responsive design for various screen sizes
    """

    def __init__(self, results_file: str, output_dir: str = 'results/graphs/'):
        """
        Initialize interactive visualizer.

        Args:
            results_file: Path to JSON results file
            output_dir: Output directory for visualizations
        """
        self.results_file = Path(results_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load data
        logger.info(f"Loading results from {results_file}")
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.df = pd.DataFrame(data)
        self.df = self.df.sort_values('error_rate')

        logger.info(f"Loaded {len(self.df)} data points")

        # Color scheme
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'success': '#06A77D',
            'danger': '#D62839',
            'background': '#F5F5F5'
        }

    def create_error_vs_distance_plot(self) -> go.Figure:
        """
        Create interactive Error Rate vs. Cosine Distance plot.

        Returns:
            Plotly Figure object
        """
        logger.info("Creating Error Rate vs. Distance plot...")

        fig = go.Figure()

        # Add line trace
        fig.add_trace(go.Scatter(
            x=self.df['error_rate'],
            y=self.df['cosine_distance'],
            mode='lines',
            name='Trend Line',
            line=dict(
                color=self.colors['primary'],
                width=3
            ),
            hovertemplate='<b>Error Rate:</b> %{x}%<br>' +
                          '<b>Cosine Distance:</b> %{y:.4f}<br>' +
                          '<extra></extra>'
        ))

        # Add scatter points
        fig.add_trace(go.Scatter(
            x=self.df['error_rate'],
            y=self.df['cosine_distance'],
            mode='markers',
            name='Data Points',
            marker=dict(
                color=self.colors['secondary'],
                size=12,
                line=dict(
                    color=self.colors['primary'],
                    width=2
                )
            ),
            text=[f"Error: {row['error_rate']}%<br>Distance: {row['cosine_distance']:.4f}"
                  for _, row in self.df.iterrows()],
            hovertemplate='<b>%{text}</b><extra></extra>'
        ))

        # Layout
        fig.update_layout(
            title={
                'text': 'Impact of Spelling Errors on Translation Quality<br>' +
                        '<sub>Cosine Distance: Original vs. Final Translation</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#333'}
            },
            xaxis_title='Spelling Error Rate (%)',
            yaxis_title='Cosine Distance',
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=10,
                gridcolor='#E0E0E0',
                showgrid=True
            ),
            yaxis=dict(
                gridcolor='#E0E0E0',
                showgrid=True,
                range=[0, max(self.df['cosine_distance']) * 1.1]
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12),
            hovermode='closest',
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#CCC',
                borderwidth=1
            ),
            width=1000,
            height=600
        )

        return fig

    def create_distance_degradation_bar(self) -> go.Figure:
        """
        Create bar chart showing distance degradation.

        Returns:
            Plotly Figure object
        """
        logger.info("Creating distance degradation bar chart...")

        # Calculate degradation
        distances = self.df['cosine_distance'].values
        error_rates = self.df['error_rate'].values
        degradation = np.diff(distances, prepend=[0])

        # Color code: green for no increase, red for increase
        colors = [self.colors['success'] if d <= 0 else self.colors['danger']
                  for d in degradation]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=error_rates,
            y=degradation,
            marker_color=colors,
            marker_line_color='#333',
            marker_line_width=1.5,
            text=[f"{d:.4f}" for d in degradation],
            textposition='outside',
            hovertemplate='<b>Error Rate:</b> %{x}%<br>' +
                          '<b>Degradation:</b> %{y:.4f}<br>' +
                          '<extra></extra>'
        ))

        fig.update_layout(
            title={
                'text': 'Marginal Distance Degradation<br><sub>Increase per Error Rate Step</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Error Rate (%)',
            yaxis_title='Distance Increase',
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=10
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            width=800,
            height=500
        )

        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="#333", line_width=1)

        return fig

    def create_statistics_table(self) -> go.Figure:
        """
        Create interactive statistics summary table.

        Returns:
            Plotly Figure object
        """
        logger.info("Creating statistics table...")

        distances = self.df['cosine_distance'].values
        similarities = self.df['cosine_similarity'].values

        # Calculate statistics
        stats_data = {
            'Metric': [
                'Min Distance',
                'Max Distance',
                'Mean Distance',
                'Std Deviation',
                'Total Increase',
                'Min Similarity',
                'Max Similarity',
                'Mean Similarity',
                'Data Points'
            ],
            'Value': [
                f"{distances.min():.4f}",
                f"{distances.max():.4f}",
                f"{distances.mean():.4f}",
                f"{distances.std():.4f}",
                f"{distances[-1] - distances[0]:.4f}",
                f"{similarities.min():.4f}",
                f"{similarities.max():.4f}",
                f"{similarities.mean():.4f}",
                str(len(self.df))
            ]
        }

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Metric</b>', '<b>Value</b>'],
                fill_color=self.colors['primary'],
                font=dict(color='white', size=14),
                align='left',
                height=40
            ),
            cells=dict(
                values=[stats_data['Metric'], stats_data['Value']],
                fill_color=[['white', '#F5F5F5'] * 5],
                font=dict(size=12),
                align='left',
                height=35
            )
        )])

        fig.update_layout(
            title={
                'text': 'Summary Statistics',
                'x': 0.5,
                'xanchor': 'center'
            },
            width=600,
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig

    def create_sentence_length_analysis(self) -> go.Figure:
        """
        Create sentence length analysis visualization.

        Returns:
            Plotly Figure object
        """
        logger.info("Creating sentence length analysis...")

        # Calculate lengths
        original_lengths = [len(str(s).split()) for s in self.df['original_sentence']]
        final_lengths = [len(str(s).split()) for s in self.df['final_sentence']]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.df['error_rate'],
            y=original_lengths,
            mode='lines+markers',
            name='Original Length',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=self.df['error_rate'],
            y=final_lengths,
            mode='lines+markers',
            name='Final Length',
            line=dict(color=self.colors['accent'], width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title={
                'text': 'Sentence Length Comparison<br><sub>Original vs. Final Translation</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Error Rate (%)',
            yaxis_title='Word Count',
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=800,
            height=500,
            hovermode='x unified'
        )

        return fig

    def create_dashboard(self) -> go.Figure:
        """
        Create comprehensive dashboard with multiple panels.

        Returns:
            Plotly Figure object with subplots
        """
        logger.info("Creating comprehensive dashboard...")

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Error Rate vs. Cosine Distance',
                'Distance vs. Similarity',
                'Marginal Degradation',
                'Summary Statistics'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'scatter'}],
                [{'type': 'bar'}, {'type': 'table'}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )

        # 1. Error Rate vs. Distance
        fig.add_trace(
            go.Scatter(
                x=self.df['error_rate'],
                y=self.df['cosine_distance'],
                mode='lines+markers',
                name='Cosine Distance',
                line=dict(color=self.colors['primary'], width=2),
                marker=dict(size=8, color=self.colors['secondary'])
            ),
            row=1, col=1
        )

        # 2. Distance vs. Similarity
        fig.add_trace(
            go.Scatter(
                x=self.df['cosine_distance'],
                y=self.df['cosine_similarity'],
                mode='markers',
                name='Distance-Similarity',
                marker=dict(
                    size=10,
                    color=self.df['error_rate'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title='Error %', x=0.46)
                ),
                text=[f"Error: {row['error_rate']}%" for _, row in self.df.iterrows()]
            ),
            row=1, col=2
        )

        # 3. Marginal Degradation
        distances = self.df['cosine_distance'].values
        degradation = np.diff(distances, prepend=[0])
        colors_bar = [self.colors['success'] if d <= 0 else self.colors['danger']
                      for d in degradation]

        fig.add_trace(
            go.Bar(
                x=self.df['error_rate'],
                y=degradation,
                name='Degradation',
                marker_color=colors_bar,
                showlegend=False
            ),
            row=2, col=1
        )

        # 4. Statistics Table
        distances = self.df['cosine_distance'].values
        stats_data = {
            'Metric': ['Min', 'Max', 'Mean', 'Std', 'Range'],
            'Value': [
                f"{distances.min():.4f}",
                f"{distances.max():.4f}",
                f"{distances.mean():.4f}",
                f"{distances.std():.4f}",
                f"{distances.max() - distances.min():.4f}"
            ]
        }

        fig.add_trace(
            go.Table(
                header=dict(
                    values=['<b>Metric</b>', '<b>Value</b>'],
                    fill_color=self.colors['primary'],
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[stats_data['Metric'], stats_data['Value']],
                    fill_color='white',
                    font=dict(size=11)
                )
            ),
            row=2, col=2
        )

        # Update axes
        fig.update_xaxes(title_text="Error Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="Cosine Distance", row=1, col=1)

        fig.update_xaxes(title_text="Cosine Distance", row=1, col=2)
        fig.update_yaxes(title_text="Cosine Similarity", row=1, col=2)

        fig.update_xaxes(title_text="Error Rate (%)", row=2, col=1)
        fig.update_yaxes(title_text="Degradation", row=2, col=1)

        # Overall layout
        fig.update_layout(
            title_text="Translation Error Propagation Dashboard",
            title_x=0.5,
            title_font_size=20,
            showlegend=True,
            height=900,
            width=1400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        return fig

    def save_figure(
        self,
        fig: go.Figure,
        filename: str,
        formats: List[str] = ['html', 'png']
    ):
        """
        Save figure in multiple formats.

        Args:
            fig: Plotly Figure object
            filename: Base filename (without extension)
            formats: List of formats ('html', 'png', 'svg', 'pdf')
        """
        base_path = self.output_dir / filename

        for fmt in formats:
            output_file = base_path.with_suffix(f'.{fmt}')

            if fmt == 'html':
                fig.write_html(
                    str(output_file),
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                    }
                )
                logger.info(f"Saved interactive HTML: {output_file}")

            elif fmt == 'png':
                try:
                    fig.write_image(str(output_file), width=1200, height=800, scale=2)
                    logger.info(f"Saved PNG: {output_file}")
                except Exception as e:
                    logger.warning(f"Could not save PNG (install kaleido): {e}")

            elif fmt == 'svg':
                try:
                    fig.write_image(str(output_file))
                    logger.info(f"Saved SVG: {output_file}")
                except Exception as e:
                    logger.warning(f"Could not save SVG: {e}")

            elif fmt == 'pdf':
                try:
                    fig.write_image(str(output_file))
                    logger.info(f"Saved PDF: {output_file}")
                except Exception as e:
                    logger.warning(f"Could not save PDF: {e}")

    def generate_all_visualizations(self):
        """Generate all visualizations and save in multiple formats."""
        logger.info("Generating all visualizations...")

        # 1. Main error vs distance plot
        fig1 = self.create_error_vs_distance_plot()
        self.save_figure(fig1, 'interactive_error_vs_distance', ['html', 'png'])

        # 2. Distance degradation bar
        fig2 = self.create_distance_degradation_bar()
        self.save_figure(fig2, 'interactive_degradation_bar', ['html', 'png'])

        # 3. Statistics table
        fig3 = self.create_statistics_table()
        self.save_figure(fig3, 'interactive_statistics_table', ['html'])

        # 4. Sentence length analysis
        fig4 = self.create_sentence_length_analysis()
        self.save_figure(fig4, 'interactive_sentence_length', ['html', 'png'])

        # 5. Comprehensive dashboard
        fig5 = self.create_dashboard()
        self.save_figure(fig5, 'interactive_dashboard', ['html', 'png'])

        logger.info("All visualizations generated successfully!")


def main():
    """Command-line interface for interactive visualizer."""
    parser = argparse.ArgumentParser(
        description='Create interactive visualizations from experiment results'
    )
    parser.add_argument(
        '--results',
        required=True,
        help='JSON file with experiment results'
    )
    parser.add_argument(
        '--output',
        default='results/graphs/',
        help='Output directory for visualizations'
    )
    parser.add_argument(
        '--viz-type',
        choices=['error_distance', 'degradation', 'stats', 'length', 'dashboard', 'all'],
        default='all',
        help='Type of visualization to create'
    )
    parser.add_argument(
        '--formats',
        nargs='+',
        default=['html', 'png'],
        choices=['html', 'png', 'svg', 'pdf'],
        help='Output formats'
    )

    args = parser.parse_args()

    # Initialize visualizer
    viz = InteractiveVisualizer(args.results, args.output)

    # Generate visualizations
    if args.viz_type == 'all':
        viz.generate_all_visualizations()
    elif args.viz_type == 'error_distance':
        fig = viz.create_error_vs_distance_plot()
        viz.save_figure(fig, 'interactive_error_vs_distance', args.formats)
    elif args.viz_type == 'degradation':
        fig = viz.create_distance_degradation_bar()
        viz.save_figure(fig, 'interactive_degradation_bar', args.formats)
    elif args.viz_type == 'stats':
        fig = viz.create_statistics_table()
        viz.save_figure(fig, 'interactive_statistics_table', args.formats)
    elif args.viz_type == 'length':
        fig = viz.create_sentence_length_analysis()
        viz.save_figure(fig, 'interactive_sentence_length', args.formats)
    elif args.viz_type == 'dashboard':
        fig = viz.create_dashboard()
        viz.save_figure(fig, 'interactive_dashboard', args.formats)

    logger.info("Visualization complete!")


if __name__ == '__main__':
    main()
