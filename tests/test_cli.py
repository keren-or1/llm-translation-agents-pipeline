"""
Unit tests for cli module
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from cli import parse_arguments


def test_parse_arguments_defaults():
    """Test parse_arguments with no arguments (all defaults)"""
    test_args = []

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.input is None
        assert args.output == 'docs/experiment_results.json'
        assert args.graph_output == 'screenshots/translation_distance_graph.png'
        assert args.cache_dir == '.cache'
        assert args.clear_cache is False


def test_parse_arguments_input_file():
    """Test parse_arguments with input file specified"""
    test_args = ['--input', 'custom_input.json']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.input == 'custom_input.json'


def test_parse_arguments_input_file_short():
    """Test parse_arguments with input file using short flag"""
    test_args = ['-i', 'test.json']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.input == 'test.json'


def test_parse_arguments_output_file():
    """Test parse_arguments with output file specified"""
    test_args = ['--output', 'custom_output.json']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.output == 'custom_output.json'


def test_parse_arguments_output_file_short():
    """Test parse_arguments with output file using short flag"""
    test_args = ['-o', 'results.json']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.output == 'results.json'


def test_parse_arguments_graph_output():
    """Test parse_arguments with graph output specified"""
    test_args = ['--graph-output', 'custom_graph.png']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.graph_output == 'custom_graph.png'


def test_parse_arguments_graph_output_short():
    """Test parse_arguments with graph output using short flag"""
    test_args = ['-g', 'graph.png']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.graph_output == 'graph.png'


def test_parse_arguments_cache_dir():
    """Test parse_arguments with cache directory specified"""
    test_args = ['--cache-dir', '.custom_cache']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.cache_dir == '.custom_cache'


def test_parse_arguments_cache_dir_short():
    """Test parse_arguments with cache directory using short flag"""
    test_args = ['-c', '.mycache']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.cache_dir == '.mycache'


def test_parse_arguments_clear_cache():
    """Test parse_arguments with clear cache flag"""
    test_args = ['--clear-cache']

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.clear_cache is True


def test_parse_arguments_all_options():
    """Test parse_arguments with all options specified"""
    test_args = [
        '--input', 'input.json',
        '--output', 'output.json',
        '--graph-output', 'graph.png',
        '--cache-dir', '.mycache',
        '--clear-cache'
    ]

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.input == 'input.json'
        assert args.output == 'output.json'
        assert args.graph_output == 'graph.png'
        assert args.cache_dir == '.mycache'
        assert args.clear_cache is True


def test_parse_arguments_all_options_short():
    """Test parse_arguments with all options using short flags"""
    test_args = [
        '-i', 'in.json',
        '-o', 'out.json',
        '-g', 'gr.png',
        '-c', '.cache2',
        '--clear-cache'
    ]

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.input == 'in.json'
        assert args.output == 'out.json'
        assert args.graph_output == 'gr.png'
        assert args.cache_dir == '.cache2'
        assert args.clear_cache is True


def test_parse_arguments_mixed_flags():
    """Test parse_arguments with mixed short and long flags"""
    test_args = [
        '-i', 'input.json',
        '--output', 'output.json',
        '-g', 'graph.png',
        '--cache-dir', '.cache'
    ]

    with patch('sys.argv', ['calculate_results.py'] + test_args):
        args = parse_arguments()

        assert args.input == 'input.json'
        assert args.output == 'output.json'
        assert args.graph_output == 'graph.png'
        assert args.cache_dir == '.cache'
        assert args.clear_cache is False
