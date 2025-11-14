#!/usr/bin/env python3
"""
Statistical Analyzer - Advanced statistical analysis of experiment results

This module provides comprehensive statistical analysis including:
- Correlation analysis
- Linear regression
- Distribution analysis
- Confidence intervals
- Hypothesis testing

Usage:
    python src/statistical_analyzer.py \
      --results results/analysis/experiment_results.json \
      --output results/stats_report.json
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import logging

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, spearmanr, shapiro, normaltest
import matplotlib.pyplot as plt

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StatisticalAnalyzer:
    """
    Perform advanced statistical analysis on experiment results.

    Features:
    - Correlation analysis (Pearson, Spearman)
    - Linear regression with R² and p-values
    - Distribution analysis (normality tests)
    - Confidence intervals
    - Hypothesis testing
    - Statistical summaries
    """

    def __init__(self, results_file: str):
        """
        Initialize statistical analyzer.

        Args:
            results_file: Path to experiment results JSON file
        """
        logger.info(f"Loading results from {results_file}")

        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.df = pd.DataFrame(data)
        logger.info(f"Loaded {len(self.df)} data points")

        # Extract arrays for analysis
        self.error_rates = self.df['error_rate'].astype(float).values
        self.distances = self.df['cosine_distance'].astype(float).values
        self.similarities = self.df['cosine_similarity'].astype(float).values

    def compute_correlation(self) -> Dict:
        """
        Compute correlation between error rate and distance.

        Returns:
            Dictionary with correlation statistics
        """
        logger.info("Computing correlation...")

        # Pearson correlation (linear relationship)
        pearson_r, pearson_p = pearsonr(self.error_rates, self.distances)

        # Spearman correlation (monotonic relationship)
        spearman_r, spearman_p = spearmanr(self.error_rates, self.distances)

        return {
            'pearson': {
                'correlation_coefficient': round(float(pearson_r), 6),
                'p_value': round(float(pearson_p), 6),
                'strength': self._interpret_correlation(pearson_r),
                'significant': pearson_p < 0.05
            },
            'spearman': {
                'correlation_coefficient': round(float(spearman_r), 6),
                'p_value': round(float(spearman_p), 6),
                'strength': self._interpret_correlation(spearman_r),
                'significant': spearman_p < 0.05
            }
        }

    def _interpret_correlation(self, r: float) -> str:
        """Interpret correlation coefficient strength."""
        abs_r = abs(r)
        if abs_r >= 0.9:
            return "very strong"
        elif abs_r >= 0.7:
            return "strong"
        elif abs_r >= 0.5:
            return "moderate"
        elif abs_r >= 0.3:
            return "weak"
        else:
            return "very weak"

    def compute_linear_regression(self) -> Dict:
        """
        Perform linear regression: distance = slope * error_rate + intercept

        Returns:
            Dictionary with regression statistics
        """
        logger.info("Computing linear regression...")

        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            self.error_rates,
            self.distances
        )

        # Calculate R²
        r_squared = r_value ** 2

        # Calculate predictions
        predictions = slope * self.error_rates + intercept

        # Calculate residuals
        residuals = self.distances - predictions

        # Mean squared error
        mse = np.mean(residuals ** 2)
        rmse = np.sqrt(mse)

        # Mean absolute error
        mae = np.mean(np.abs(residuals))

        return {
            'slope': round(float(slope), 6),
            'intercept': round(float(intercept), 6),
            'r_value': round(float(r_value), 6),
            'r_squared': round(float(r_squared), 6),
            'p_value': round(float(p_value), 8),
            'std_err': round(float(std_err), 6),
            'rmse': round(float(rmse), 6),
            'mae': round(float(mae), 6),
            'equation': f"distance = {slope:.6f} * error_rate + {intercept:.6f}",
            'interpretation': {
                'fit_quality': self._interpret_r_squared(r_squared),
                'significant': p_value < 0.05,
                'slope_interpretation': f"Each 1% increase in error rate increases distance by {slope:.6f}"
            }
        }

    def _interpret_r_squared(self, r_squared: float) -> str:
        """Interpret R² value."""
        if r_squared >= 0.90:
            return "excellent fit"
        elif r_squared >= 0.75:
            return "good fit"
        elif r_squared >= 0.50:
            return "moderate fit"
        elif r_squared >= 0.25:
            return "weak fit"
        else:
            return "poor fit"

    def compute_statistics_by_error_rate(self) -> Dict:
        """
        Compute statistics grouped by error rate.

        Returns:
            Dictionary with per-error-rate statistics
        """
        logger.info("Computing per-error-rate statistics...")

        stats_by_rate = {}

        for rate in sorted(self.df['error_rate'].unique()):
            subset = self.df[self.df['error_rate'] == rate]

            stats_by_rate[int(rate)] = {
                'count': len(subset),
                'distance': {
                    'mean': round(float(subset['cosine_distance'].mean()), 6),
                    'std': round(float(subset['cosine_distance'].std()), 6),
                    'min': round(float(subset['cosine_distance'].min()), 6),
                    'max': round(float(subset['cosine_distance'].max()), 6)
                },
                'similarity': {
                    'mean': round(float(subset['cosine_similarity'].mean()), 6),
                    'std': round(float(subset['cosine_similarity'].std()), 6),
                    'min': round(float(subset['cosine_similarity'].min()), 6),
                    'max': round(float(subset['cosine_similarity'].max()), 6)
                }
            }

        return stats_by_rate

    def compute_confidence_intervals(self, confidence: float = 0.95) -> Dict:
        """
        Compute confidence intervals for distance at each error rate.

        Args:
            confidence: Confidence level (default 0.95 for 95%)

        Returns:
            Dictionary with confidence intervals
        """
        logger.info(f"Computing {confidence*100:.0f}% confidence intervals...")

        intervals = {}
        alpha = 1 - confidence

        for rate in sorted(self.df['error_rate'].unique()):
            subset = self.df[self.df['error_rate'] == rate]
            distances = subset['cosine_distance'].values

            if len(distances) > 1:
                mean = np.mean(distances)
                std = np.std(distances, ddof=1)
                se = std / np.sqrt(len(distances))

                # t-distribution for small samples
                t_value = stats.t.ppf(1 - alpha/2, len(distances) - 1)
                margin = t_value * se

                intervals[int(rate)] = {
                    'mean': round(float(mean), 6),
                    'lower_bound': round(float(mean - margin), 6),
                    'upper_bound': round(float(mean + margin), 6),
                    'margin_of_error': round(float(margin), 6),
                    'confidence_level': confidence
                }
            else:
                intervals[int(rate)] = {
                    'mean': round(float(distances[0]), 6),
                    'lower_bound': None,
                    'upper_bound': None,
                    'margin_of_error': None,
                    'confidence_level': confidence,
                    'note': 'Insufficient data for CI'
                }

        return intervals

    def test_linearity_hypothesis(self) -> Dict:
        """
        Test hypothesis: Distance increases linearly with error rate.

        Returns:
            Dictionary with hypothesis test results
        """
        logger.info("Testing linearity hypothesis...")

        # Perform linear regression
        regression = self.compute_linear_regression()

        # Test if slope is significantly different from zero
        slope_significant = regression['p_value'] < 0.05

        # Test if R² is high enough (> 0.90 for strong linear)
        strong_linear = regression['r_squared'] > 0.90

        # Test residuals for normality (assumption of linear regression)
        slope, intercept = regression['slope'], regression['intercept']
        predictions = slope * self.error_rates + intercept
        residuals = self.distances - predictions

        if len(residuals) >= 3:
            # Shapiro-Wilk test for normality
            shapiro_stat, shapiro_p = shapiro(residuals)
            residuals_normal = shapiro_p > 0.05
        else:
            shapiro_stat, shapiro_p = None, None
            residuals_normal = None

        return {
            'hypothesis': 'Distance increases linearly with error rate',
            'slope_significant': slope_significant,
            'strong_linear_fit': strong_linear,
            'r_squared': regression['r_squared'],
            'p_value': regression['p_value'],
            'residuals_normal': residuals_normal,
            'shapiro_test': {
                'statistic': round(float(shapiro_stat), 6) if shapiro_stat else None,
                'p_value': round(float(shapiro_p), 6) if shapiro_p else None
            },
            'conclusion': self._linearity_conclusion(
                slope_significant,
                strong_linear,
                residuals_normal
            )
        }

    def _linearity_conclusion(
        self,
        slope_sig: bool,
        strong_fit: bool,
        residuals_normal: bool
    ) -> str:
        """Generate conclusion for linearity test."""
        if slope_sig and strong_fit:
            if residuals_normal or residuals_normal is None:
                return "ACCEPTED: Strong evidence for linear relationship"
            else:
                return "PARTIAL: Linear fit is good but residuals not normal"
        elif slope_sig:
            return "PARTIAL: Significant relationship but fit could be better"
        else:
            return "REJECTED: No significant linear relationship detected"

    def compute_distribution_analysis(self) -> Dict:
        """
        Analyze distribution of distances.

        Returns:
            Dictionary with distribution statistics
        """
        logger.info("Analyzing distribution...")

        return {
            'distance': {
                'mean': round(float(np.mean(self.distances)), 6),
                'median': round(float(np.median(self.distances)), 6),
                'std': round(float(np.std(self.distances)), 6),
                'variance': round(float(np.var(self.distances)), 6),
                'min': round(float(np.min(self.distances)), 6),
                'max': round(float(np.max(self.distances)), 6),
                'range': round(float(np.max(self.distances) - np.min(self.distances)), 6),
                'q1': round(float(np.percentile(self.distances, 25)), 6),
                'q3': round(float(np.percentile(self.distances, 75)), 6),
                'iqr': round(float(np.percentile(self.distances, 75) - np.percentile(self.distances, 25)), 6)
            },
            'similarity': {
                'mean': round(float(np.mean(self.similarities)), 6),
                'median': round(float(np.median(self.similarities)), 6),
                'std': round(float(np.std(self.similarities)), 6),
                'variance': round(float(np.var(self.similarities)), 6),
                'min': round(float(np.min(self.similarities)), 6),
                'max': round(float(np.max(self.similarities)), 6),
                'range': round(float(np.max(self.similarities) - np.min(self.similarities)), 6),
                'q1': round(float(np.percentile(self.similarities, 25)), 6),
                'q3': round(float(np.percentile(self.similarities, 75)), 6),
                'iqr': round(float(np.percentile(self.similarities, 75) - np.percentile(self.similarities, 25)), 6)
            }
        }

    def generate_comprehensive_report(self) -> Dict:
        """
        Generate comprehensive statistical report.

        Returns:
            Complete statistical analysis report
        """
        logger.info("Generating comprehensive statistical report...")

        report = {
            'metadata': {
                'analysis_date': pd.Timestamp.now().isoformat(),
                'data_points': len(self.df),
                'error_rates_tested': sorted(self.error_rates.tolist())
            },
            'correlation_analysis': self.compute_correlation(),
            'linear_regression': self.compute_linear_regression(),
            'statistics_by_error_rate': self.compute_statistics_by_error_rate(),
            'confidence_intervals': self.compute_confidence_intervals(0.95),
            'linearity_hypothesis_test': self.test_linearity_hypothesis(),
            'distribution_analysis': self.compute_distribution_analysis()
        }

        return report

    def save_report(self, output_file: str):
        """
        Save statistical report to JSON file.

        Args:
            output_file: Path to output file
        """
        report = self.generate_comprehensive_report()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved statistical report to {output_file}")

    def create_diagnostic_plots(self, output_dir: str):
        """
        Create diagnostic plots for regression analysis.

        Args:
            output_dir: Directory to save plots
        """
        logger.info("Creating diagnostic plots...")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Compute regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            self.error_rates,
            self.distances
        )
        predictions = slope * self.error_rates + intercept
        residuals = self.distances - predictions

        # Create 2x2 diagnostic plot
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Regression Diagnostic Plots', fontsize=16, fontweight='bold')

        # 1. Fitted vs Actual
        ax1 = axes[0, 0]
        ax1.scatter(predictions, self.distances, alpha=0.6, s=100)
        ax1.plot([predictions.min(), predictions.max()],
                [predictions.min(), predictions.max()],
                'r--', lw=2)
        ax1.set_xlabel('Fitted Values')
        ax1.set_ylabel('Actual Values')
        ax1.set_title('Fitted vs Actual')
        ax1.grid(True, alpha=0.3)

        # 2. Residuals vs Fitted
        ax2 = axes[0, 1]
        ax2.scatter(predictions, residuals, alpha=0.6, s=100)
        ax2.axhline(y=0, color='r', linestyle='--', lw=2)
        ax2.set_xlabel('Fitted Values')
        ax2.set_ylabel('Residuals')
        ax1.set_title(f'Residuals vs Fitted (R²={r_value**2:.4f})')
        ax2.grid(True, alpha=0.3)

        # 3. Q-Q Plot
        ax3 = axes[1, 0]
        stats.probplot(residuals, dist="norm", plot=ax3)
        ax3.set_title('Q-Q Plot (Normality Check)')
        ax3.grid(True, alpha=0.3)

        # 4. Residual Histogram
        ax4 = axes[1, 1]
        ax4.hist(residuals, bins=10, edgecolor='black', alpha=0.7)
        ax4.set_xlabel('Residuals')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Residual Distribution')
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(output_path / 'regression_diagnostics.png', dpi=300, bbox_inches='tight')
        logger.info(f"Saved diagnostic plots to {output_path / 'regression_diagnostics.png'}")
        plt.close()


def main():
    """Command-line interface for statistical analyzer."""
    parser = argparse.ArgumentParser(
        description='Perform statistical analysis on experiment results'
    )
    parser.add_argument(
        '--results',
        required=True,
        help='JSON file with experiment results'
    )
    parser.add_argument(
        '--output',
        default='results/stats_report.json',
        help='Output file for statistical report'
    )
    parser.add_argument(
        '--plots',
        help='Directory to save diagnostic plots'
    )
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.95,
        help='Confidence level for intervals (default 0.95)'
    )

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = StatisticalAnalyzer(args.results)

    # Generate and save report
    analyzer.save_report(args.output)

    # Print summary
    report = analyzer.generate_comprehensive_report()
    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS SUMMARY")
    print("="*60)
    print(f"\nData Points: {report['metadata']['data_points']}")
    print(f"Error Rates: {report['metadata']['error_rates_tested']}")

    print("\nLinear Regression:")
    reg = report['linear_regression']
    print(f"  Equation: {reg['equation']}")
    print(f"  R² = {reg['r_squared']:.4f} ({reg['interpretation']['fit_quality']})")
    print(f"  p-value = {reg['p_value']:.8f}")

    print("\nCorrelation:")
    corr = report['correlation_analysis']['pearson']
    print(f"  Pearson r = {corr['correlation_coefficient']:.4f} ({corr['strength']})")
    print(f"  Significant: {corr['significant']}")

    print("\nLinearity Test:")
    hyp = report['linearity_hypothesis_test']
    print(f"  Conclusion: {hyp['conclusion']}")

    print("\n" + "="*60)

    # Create diagnostic plots if requested
    if args.plots:
        analyzer.create_diagnostic_plots(args.plots)

    logger.info("Statistical analysis complete!")


if __name__ == '__main__':
    main()
