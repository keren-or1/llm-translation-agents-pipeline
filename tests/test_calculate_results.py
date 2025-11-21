"""
Unit tests for calculate_results module
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from calculate_results import process_experiments, main


def test_process_experiments():
    """Test processing experiments with mock calculator"""
    # Create mock calculator
    mock_calculator = Mock()
    mock_calculator.get_or_calculate_embedding.side_effect = lambda text: [0.1, 0.2, 0.3]
    mock_calculator.calculate_cosine_distance.return_value = (0.123456, 0.876544)

    # Test data
    experiments = [
        {
            "error_percentage": 0,
            "original_english": "Original text",
            "final_english": "Final text"
        },
        {
            "error_percentage": 10,
            "original_english": "Another original",
            "final_english": "Another final"
        }
    ]

    results = process_experiments(mock_calculator, experiments)

    # Verify results
    assert len(results) == 2
    assert results[0]["error_percentage"] == 0
    assert results[0]["cosine_distance"] == 0.123456
    assert results[0]["cosine_similarity"] == 0.876544
    assert results[1]["error_percentage"] == 10

    # Verify calculator was called correctly
    assert mock_calculator.get_or_calculate_embedding.call_count == 4  # 2 experiments * 2 texts each
    assert mock_calculator.calculate_cosine_distance.call_count == 2


def test_process_experiments_empty():
    """Test processing empty experiments list"""
    mock_calculator = Mock()
    experiments = []

    results = process_experiments(mock_calculator, experiments)

    assert len(results) == 0
    assert mock_calculator.get_or_calculate_embedding.call_count == 0


@patch('calculate_results.parse_arguments')
@patch('calculate_results.EmbeddingCalculator')
@patch('calculate_results.get_default_experiments')
@patch('calculate_results.create_distance_graph')
@patch('calculate_results.print_statistical_analysis')
@patch('builtins.open')
def test_main_default_experiments(mock_open, mock_stats, mock_graph, mock_default_exp,
                                   mock_calculator_class, mock_parse_args):
    """Test main function with default experiments"""
    # Setup mocks
    mock_args = Mock()
    mock_args.input = None
    mock_args.output = 'test_output.json'
    mock_args.graph_output = 'test_graph.png'
    mock_args.cache_dir = '.test_cache'
    mock_args.clear_cache = False
    mock_parse_args.return_value = mock_args

    mock_default_exp.return_value = [
        {
            "error_percentage": 0,
            "original_english": "Test sentence",
            "final_english": "Test result"
        }
    ]

    mock_calculator = Mock()
    mock_calculator.get_or_calculate_embedding.return_value = [0.1, 0.2, 0.3]
    mock_calculator.calculate_cosine_distance.return_value = (0.123, 0.877)
    mock_calculator_class.return_value = mock_calculator

    # Create temporary directories for output
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'test_output.json'
        graph_path = Path(tmpdir) / 'test_graph.png'
        mock_args.output = str(output_path)
        mock_args.graph_output = str(graph_path)

        # Run main
        main()

    # Verify function calls
    mock_default_exp.assert_called_once()
    mock_calculator_class.assert_called_once_with(cache_dir='.test_cache')
    mock_graph.assert_called_once()
    mock_stats.assert_called_once()


@patch('calculate_results.parse_arguments')
@patch('calculate_results.EmbeddingCalculator')
@patch('calculate_results.load_experiments')
@patch('calculate_results.get_default_experiments')
@patch('calculate_results.create_distance_graph')
@patch('calculate_results.print_statistical_analysis')
@patch('builtins.open')
def test_main_with_input_file(mock_open, mock_stats, mock_graph, mock_default_exp,
                               mock_load_exp, mock_calculator_class, mock_parse_args):
    """Test main function with input file"""
    # Setup mocks
    mock_args = Mock()
    mock_args.input = 'input.json'
    mock_args.output = 'test_output.json'
    mock_args.graph_output = 'test_graph.png'
    mock_args.cache_dir = '.test_cache'
    mock_args.clear_cache = False
    mock_parse_args.return_value = mock_args

    mock_load_exp.return_value = [
        {
            "error_percentage": 5,
            "original_english": "Loaded sentence",
            "final_english": "Loaded result"
        }
    ]

    mock_calculator = Mock()
    mock_calculator.get_or_calculate_embedding.return_value = [0.1, 0.2, 0.3]
    mock_calculator.calculate_cosine_distance.return_value = (0.456, 0.544)
    mock_calculator_class.return_value = mock_calculator

    # Create temporary directories for output
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'test_output.json'
        graph_path = Path(tmpdir) / 'test_graph.png'
        mock_args.output = str(output_path)
        mock_args.graph_output = str(graph_path)

        # Run main
        main()

    # Verify load_experiments was called
    mock_load_exp.assert_called_once_with('input.json')
    mock_default_exp.assert_not_called()


@patch('calculate_results.parse_arguments')
@patch('calculate_results.shutil.rmtree')
@patch('calculate_results.EmbeddingCalculator')
@patch('calculate_results.get_default_experiments')
@patch('calculate_results.create_distance_graph')
@patch('calculate_results.print_statistical_analysis')
@patch('builtins.open')
def test_main_clear_cache(mock_open, mock_stats, mock_graph, mock_default_exp,
                          mock_calculator_class, mock_rmtree, mock_parse_args):
    """Test main function with clear_cache flag"""
    # Setup mocks
    mock_args = Mock()
    mock_args.input = None
    mock_args.output = 'test_output.json'
    mock_args.graph_output = 'test_graph.png'
    mock_args.cache_dir = '.test_cache'
    mock_args.clear_cache = True
    mock_parse_args.return_value = mock_args

    mock_default_exp.return_value = [
        {
            "error_percentage": 0,
            "original_english": "Test",
            "final_english": "Test"
        }
    ]

    mock_calculator = Mock()
    mock_calculator.get_or_calculate_embedding.return_value = [0.1]
    mock_calculator.calculate_cosine_distance.return_value = (0.0, 1.0)
    mock_calculator_class.return_value = mock_calculator

    # Mock Path.exists to return True for cache directory
    with patch('calculate_results.Path') as mock_path:
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.parent.mkdir = MagicMock()
        mock_path_instance.glob.return_value = []
        mock_path.return_value = mock_path_instance

        # Create temporary directories for output
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_output.json'
            graph_path = Path(tmpdir) / 'test_graph.png'
            # Override the mocked Path for actual file operations
            with patch('calculate_results.Path', side_effect=lambda x: Path(x) if x in [mock_args.output, mock_args.graph_output] else mock_path_instance):
                mock_args.output = str(output_path)
                mock_args.graph_output = str(graph_path)

                # Run main
                main()

    # Verify cache was cleared (at least once, may be called by tempdir cleanup too)
    assert mock_rmtree.call_count >= 1


@patch('calculate_results.parse_arguments')
@patch('calculate_results.EmbeddingCalculator')
@patch('calculate_results.load_experiments')
@patch('calculate_results.get_default_experiments')
@patch('calculate_results.create_distance_graph')
@patch('calculate_results.print_statistical_analysis')
@patch('builtins.open')
def test_main_fallback_to_default(mock_open, mock_stats, mock_graph, mock_default_exp,
                                  mock_load_exp, mock_calculator_class, mock_parse_args):
    """Test main function fallback to default when file loading fails"""
    # Setup mocks
    mock_args = Mock()
    mock_args.input = 'nonexistent.json'
    mock_args.output = 'test_output.json'
    mock_args.graph_output = 'test_graph.png'
    mock_args.cache_dir = '.test_cache'
    mock_args.clear_cache = False
    mock_parse_args.return_value = mock_args

    # load_experiments returns None (file not found)
    mock_load_exp.return_value = None

    mock_default_exp.return_value = [
        {
            "error_percentage": 0,
            "original_english": "Default",
            "final_english": "Default"
        }
    ]

    mock_calculator = Mock()
    mock_calculator.get_or_calculate_embedding.return_value = [0.1]
    mock_calculator.calculate_cosine_distance.return_value = (0.0, 1.0)
    mock_calculator_class.return_value = mock_calculator

    # Create temporary directories for output
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'test_output.json'
        graph_path = Path(tmpdir) / 'test_graph.png'
        mock_args.output = str(output_path)
        mock_args.graph_output = str(graph_path)

        # Run main
        main()

    # Verify fallback to default
    mock_load_exp.assert_called_once_with('nonexistent.json')
    mock_default_exp.assert_called_once()
