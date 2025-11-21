"""
Unit tests for visualization module
"""

import pytest
import sys
from pathlib import Path
import tempfile
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from visualization import create_distance_graph


@pytest.fixture
def sample_results():
    """Create sample results for testing"""
    return [
        {"error_percentage": 0, "cosine_distance": 0.1, "cosine_similarity": 0.9},
        {"error_percentage": 10, "cosine_distance": 0.2, "cosine_similarity": 0.8},
        {"error_percentage": 20, "cosine_distance": 0.3, "cosine_similarity": 0.7},
        {"error_percentage": 30, "cosine_distance": 0.4, "cosine_similarity": 0.6},
        {"error_percentage": 40, "cosine_distance": 0.5, "cosine_similarity": 0.5},
        {"error_percentage": 50, "cosine_distance": 0.6, "cosine_similarity": 0.4}
    ]


def test_create_distance_graph_creates_file(sample_results):
    """Test that graph file is created"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_graph.png"

        fig = create_distance_graph(sample_results, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0  # File has content

        plt.close(fig)


def test_create_distance_graph_returns_figure(sample_results):
    """Test that function returns matplotlib Figure"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_graph.png"

        fig = create_distance_graph(sample_results, str(output_path))

        assert isinstance(fig, matplotlib.figure.Figure)

        plt.close(fig)


def test_create_distance_graph_has_two_subplots(sample_results):
    """Test that graph has two subplots (distance and similarity)"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_graph.png"

        fig = create_distance_graph(sample_results, str(output_path))

        axes = fig.get_axes()
        assert len(axes) == 2  # Two subplots

        plt.close(fig)


def test_create_distance_graph_with_single_result():
    """Test graph creation with single data point"""
    results = [{"error_percentage": 0, "cosine_distance": 0.1, "cosine_similarity": 0.9}]

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_graph.png"

        fig = create_distance_graph(results, str(output_path))

        assert output_path.exists()

        plt.close(fig)


def test_create_distance_graph_handles_varying_distances():
    """Test graph with extreme distance values"""
    results = [
        {"error_percentage": 0, "cosine_distance": 0.0, "cosine_similarity": 1.0},
        {"error_percentage": 50, "cosine_distance": 1.0, "cosine_similarity": 0.0}
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_graph.png"

        fig = create_distance_graph(results, str(output_path))

        assert output_path.exists()

        plt.close(fig)


def test_create_distance_graph_creates_high_res_image(sample_results):
    """Test that graph is saved with high resolution (300 DPI)"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_graph.png"

        fig = create_distance_graph(sample_results, str(output_path))

        # File should be reasonably large (high DPI)
        file_size = output_path.stat().st_size
        assert file_size > 50000  # At least 50KB for 300 DPI image

        plt.close(fig)


def test_create_distance_graph_default_output_path(sample_results):
    """Test graph creation with default output path"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory to avoid creating files in project root
        import os
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:
            fig = create_distance_graph(sample_results)

            # Check default filename
            default_path = Path("translation_distance_graph.png")
            assert default_path.exists()

        finally:
            os.chdir(original_dir)
            plt.close(fig)
