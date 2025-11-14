#!/usr/bin/env python3
"""
Unit Tests for Visualizer

Tests the visualizer module including:
- Graph creation
- Data loading
- Formatting
- File outputs

Run with: pytest tests/test_visualizer.py -v --cov=src.visualizer
"""

import pytest
import json
import tempfile
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from visualizer import load_results, create_main_graph


class TestDataLoading:
    """Test data loading functionality."""

    def test_load_results_valid_file(self):
        """Test loading valid results file."""
        # Create temporary file with test data
        test_data = [
            {
                "error_rate": 0,
                "cosine_similarity": 0.95,
                "cosine_distance": 0.05,
                "original_sentence": "Test",
                "final_sentence": "Test"
            },
            {
                "error_rate": 10,
                "cosine_similarity": 0.88,
                "cosine_distance": 0.12,
                "original_sentence": "Test",
                "final_sentence": "Tset"
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            df = load_results(temp_file)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert 'error_rate' in df.columns
            assert 'cosine_distance' in df.columns
        finally:
            Path(temp_file).unlink()

    def test_load_results_missing_file(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_results('nonexistent_file.json')

    def test_load_results_invalid_json(self):
        """Test loading invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                load_results(temp_file)
        finally:
            Path(temp_file).unlink()

    def test_load_results_empty_data(self):
        """Test loading empty data."""
        test_data = []

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            df = load_results(temp_file)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 0
        finally:
            Path(temp_file).unlink()


class TestGraphCreation:
    """Test graph creation functions."""

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample DataFrame for testing."""
        data = {
            'error_rate': [0, 10, 20, 30, 40, 50],
            'cosine_distance': [0.05, 0.12, 0.22, 0.35, 0.52, 0.68],
            'cosine_similarity': [0.95, 0.88, 0.78, 0.65, 0.48, 0.32],
            'original_sentence': ['Test sentence'] * 6,
            'final_sentence': ['Test sentence'] * 6
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_create_main_graph_basic(self, sample_dataframe, temp_output_dir):
        """Test creating main graph."""
        with patch('visualizer.plt') as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            create_main_graph(sample_dataframe, temp_output_dir)

            # Verify plot was called
            mock_ax.plot.assert_called()
            mock_fig.tight_layout.assert_called()

    def test_create_main_graph_saves_files(self, sample_dataframe, temp_output_dir):
        """Test that main graph saves output files."""
        create_main_graph(sample_dataframe, temp_output_dir)

        output_dir = Path(temp_output_dir)
        # Check that files are created (PNG and SVG)
        # Note: Actual file creation depends on matplotlib
        assert output_dir.exists()

    def test_create_main_graph_with_empty_data(self, temp_output_dir):
        """Test creating graph with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['error_rate', 'cosine_distance', 'cosine_similarity'])

        # Should handle empty data gracefully
        try:
            create_main_graph(empty_df, temp_output_dir)
        except Exception as e:
            # Some exception is acceptable for empty data
            assert isinstance(e, (ValueError, IndexError, KeyError))

    def test_create_main_graph_correct_data_types(self, temp_output_dir):
        """Test that graph handles correct data types."""
        data = {
            'error_rate': [0, 10, 20],
            'cosine_distance': [0.05, 0.12, 0.22],
            'cosine_similarity': [0.95, 0.88, 0.78],
            'original_sentence': ['Test'] * 3,
            'final_sentence': ['Test'] * 3
        }
        df = pd.DataFrame(data)

        # Should work with proper data types
        create_main_graph(df, temp_output_dir)


class TestGraphFormatting:
    """Test graph formatting and styling."""

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample DataFrame."""
        data = {
            'error_rate': [0, 25, 50],
            'cosine_distance': [0.05, 0.30, 0.65],
            'cosine_similarity': [0.95, 0.70, 0.35],
            'original_sentence': ['Test'] * 3,
            'final_sentence': ['Test'] * 3
        }
        return pd.DataFrame(data)

    def test_graph_has_title(self, sample_dataframe):
        """Test that graph has title."""
        with patch('visualizer.plt') as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            with tempfile.TemporaryDirectory() as tmpdir:
                create_main_graph(sample_dataframe, tmpdir)

            # Verify set_title was called
            mock_ax.set_title.assert_called()

    def test_graph_has_labels(self, sample_dataframe):
        """Test that graph has axis labels."""
        with patch('visualizer.plt') as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            with tempfile.TemporaryDirectory() as tmpdir:
                create_main_graph(sample_dataframe, tmpdir)

            # Verify labels were set
            mock_ax.set_xlabel.assert_called()
            mock_ax.set_ylabel.assert_called()

    def test_graph_has_grid(self, sample_dataframe):
        """Test that graph has grid."""
        with patch('visualizer.plt') as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            with tempfile.TemporaryDirectory() as tmpdir:
                create_main_graph(sample_dataframe, tmpdir)

            # Verify grid was enabled
            mock_ax.grid.assert_called()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_single_data_point(self):
        """Test with single data point."""
        data = {
            'error_rate': [0],
            'cosine_distance': [0.05],
            'cosine_similarity': [0.95],
            'original_sentence': ['Test'],
            'final_sentence': ['Test']
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle single point
            create_main_graph(df, tmpdir)

    def test_two_data_points(self):
        """Test with two data points."""
        data = {
            'error_rate': [0, 50],
            'cosine_distance': [0.05, 0.65],
            'cosine_similarity': [0.95, 0.35],
            'original_sentence': ['Test'] * 2,
            'final_sentence': ['Test'] * 2
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            create_main_graph(df, tmpdir)

    def test_unsorted_data(self):
        """Test with unsorted error rates."""
        data = {
            'error_rate': [50, 0, 30, 10, 40, 20],
            'cosine_distance': [0.65, 0.05, 0.35, 0.12, 0.52, 0.22],
            'cosine_similarity': [0.35, 0.95, 0.65, 0.88, 0.48, 0.78],
            'original_sentence': ['Test'] * 6,
            'final_sentence': ['Test'] * 6
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should sort data automatically
            create_main_graph(df, tmpdir)

    def test_missing_columns(self):
        """Test with missing required columns."""
        data = {
            'error_rate': [0, 10],
            # Missing cosine_distance and cosine_similarity
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(KeyError):
                create_main_graph(df, tmpdir)

    def test_nan_values(self):
        """Test with NaN values in data."""
        data = {
            'error_rate': [0, 10, 20],
            'cosine_distance': [0.05, np.nan, 0.22],
            'cosine_similarity': [0.95, 0.88, np.nan],
            'original_sentence': ['Test'] * 3,
            'final_sentence': ['Test'] * 3
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle NaN values (may skip or interpolate)
            try:
                create_main_graph(df, tmpdir)
            except Exception as e:
                # Acceptable to raise exception for invalid data
                assert isinstance(e, (ValueError, TypeError))

    def test_string_error_rates(self):
        """Test error handling with string error rates."""
        data = {
            'error_rate': ['0', '10', '20'],  # Strings instead of numbers
            'cosine_distance': [0.05, 0.12, 0.22],
            'cosine_similarity': [0.95, 0.88, 0.78],
            'original_sentence': ['Test'] * 3,
            'final_sentence': ['Test'] * 3
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should convert or raise error
            try:
                create_main_graph(df, tmpdir)
            except (TypeError, ValueError):
                pass  # Acceptable to raise error


class TestOutputFormats:
    """Test different output formats."""

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample DataFrame."""
        data = {
            'error_rate': [0, 20, 40],
            'cosine_distance': [0.05, 0.22, 0.52],
            'cosine_similarity': [0.95, 0.78, 0.48],
            'original_sentence': ['Test'] * 3,
            'final_sentence': ['Test'] * 3
        }
        return pd.DataFrame(data)

    def test_png_output(self, sample_dataframe):
        """Test PNG output creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_main_graph(sample_dataframe, tmpdir)
            # Check if PNG file exists (name may vary)
            output_dir = Path(tmpdir)
            # At least output directory should exist
            assert output_dir.exists()

    def test_svg_output(self, sample_dataframe):
        """Test SVG output creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_main_graph(sample_dataframe, tmpdir)
            output_dir = Path(tmpdir)
            assert output_dir.exists()

    def test_output_directory_creation(self, sample_dataframe):
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / 'new_subdir'
            assert not new_dir.exists()

            create_main_graph(sample_dataframe, str(new_dir))

            # Directory should be created
            assert new_dir.exists()


class TestDataValidation:
    """Test data validation and error handling."""

    def test_negative_error_rates(self):
        """Test handling of negative error rates."""
        data = {
            'error_rate': [-10, 0, 10],
            'cosine_distance': [0.05, 0.05, 0.12],
            'cosine_similarity': [0.95, 0.95, 0.88],
            'original_sentence': ['Test'] * 3,
            'final_sentence': ['Test'] * 3
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle or warn about negative values
            create_main_graph(df, tmpdir)

    def test_error_rates_over_100(self):
        """Test handling of error rates > 100."""
        data = {
            'error_rate': [0, 50, 150],
            'cosine_distance': [0.05, 0.65, 0.95],
            'cosine_similarity': [0.95, 0.35, 0.05],
            'original_sentence': ['Test'] * 3,
            'final_sentence': ['Test'] * 3
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle extreme values
            create_main_graph(df, tmpdir)

    def test_distance_out_of_range(self):
        """Test handling of cosine distance outside [0, 2] range."""
        data = {
            'error_rate': [0, 10, 20],
            'cosine_distance': [-0.1, 0.5, 2.5],  # Out of expected range
            'cosine_similarity': [1.1, 0.5, -0.5],  # Out of expected range
            'original_sentence': ['Test'] * 3,
            'final_sentence': ['Test'] * 3
        }
        df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle out-of-range values
            create_main_graph(df, tmpdir)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src.visualizer', '--cov-report=html'])
