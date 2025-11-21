"""
Unit tests for statistics module
"""

import pytest
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from statistics import print_statistical_analysis


def test_print_statistical_analysis_basic():
    """Test print_statistical_analysis with basic results"""
    results = [
        {
            "error_percentage": 0,
            "cosine_distance": 0.1
        },
        {
            "error_percentage": 10,
            "cosine_distance": 0.2
        },
        {
            "error_percentage": 20,
            "cosine_distance": 0.3
        }
    ]

    # Capture stdout
    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_statistical_analysis(results)
        output = fake_out.getvalue()

    # Verify output contains expected sections
    assert "STATISTICAL ANALYSIS" in output
    assert "Minimum distance:" in output
    assert "Maximum distance:" in output
    assert "Average distance:" in output
    assert "Std deviation:" in output
    assert "Distance Change Analysis:" in output
    assert "0.100000" in output  # min distance
    assert "0.300000" in output  # max distance


def test_print_statistical_analysis_single_result():
    """Test print_statistical_analysis with single result"""
    results = [
        {
            "error_percentage": 0,
            "cosine_distance": 0.5
        }
    ]

    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_statistical_analysis(results)
        output = fake_out.getvalue()

    # Verify basic statistics
    assert "Minimum distance:  0.500000" in output
    assert "Maximum distance:  0.500000" in output
    assert "Average distance:  0.500000" in output
    assert "Std deviation:     0.000000" in output
    # No change analysis for single result
    assert "→" not in output


def test_print_statistical_analysis_distance_changes():
    """Test print_statistical_analysis distance change calculations"""
    results = [
        {
            "error_percentage": 0,
            "cosine_distance": 0.1
        },
        {
            "error_percentage": 10,
            "cosine_distance": 0.15
        },
        {
            "error_percentage": 20,
            "cosine_distance": 0.3
        }
    ]

    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_statistical_analysis(results)
        output = fake_out.getvalue()

    # Verify distance changes are shown
    assert "0% → 10%" in output
    assert "10% → 20%" in output
    assert "+0.050000" in output  # 0.15 - 0.1
    assert "+50.00%" in output  # (0.05 / 0.1) * 100


def test_print_statistical_analysis_decreasing_distances():
    """Test print_statistical_analysis with decreasing distances"""
    results = [
        {
            "error_percentage": 0,
            "cosine_distance": 0.5
        },
        {
            "error_percentage": 10,
            "cosine_distance": 0.3
        }
    ]

    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_statistical_analysis(results)
        output = fake_out.getvalue()

    # Verify negative change is shown
    assert "-0.200000" in output
    assert "-40.00%" in output


def test_print_statistical_analysis_zero_distance():
    """Test print_statistical_analysis with zero distance edge case"""
    results = [
        {
            "error_percentage": 0,
            "cosine_distance": 0.0
        },
        {
            "error_percentage": 10,
            "cosine_distance": 0.1
        }
    ]

    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_statistical_analysis(results)
        output = fake_out.getvalue()

    # Verify it handles zero distance in percentage calculation
    assert "Minimum distance:  0.000000" in output
    assert "0% → 10%" in output


def test_print_statistical_analysis_varying_distances():
    """Test print_statistical_analysis with realistic varying distances"""
    results = [
        {
            "error_percentage": 0,
            "cosine_distance": 0.012345
        },
        {
            "error_percentage": 10,
            "cosine_distance": 0.123456
        },
        {
            "error_percentage": 20,
            "cosine_distance": 0.234567
        },
        {
            "error_percentage": 30,
            "cosine_distance": 0.345678
        }
    ]

    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_statistical_analysis(results)
        output = fake_out.getvalue()

    # Verify min/max are correct
    assert "0.012345" in output  # minimum
    assert "0.345678" in output  # maximum
    # Verify all error percentages appear in change analysis
    assert "0% → 10%" in output
    assert "10% → 20%" in output
    assert "20% → 30%" in output


def test_print_statistical_analysis_large_dataset():
    """Test print_statistical_analysis with larger dataset"""
    results = [
        {"error_percentage": i * 10, "cosine_distance": i * 0.05}
        for i in range(11)  # 0%, 10%, ..., 100%
    ]

    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_statistical_analysis(results)
        output = fake_out.getvalue()

    # Verify basic statistics work with larger dataset
    assert "Minimum distance:  0.000000" in output
    assert "Maximum distance:  0.500000" in output
    assert "STATISTICAL ANALYSIS" in output
    assert "Distance Change Analysis:" in output
    # Should have 10 change entries (11 results = 10 transitions)
    assert output.count("→") == 10


def test_print_statistical_analysis_output_format():
    """Test print_statistical_analysis output formatting"""
    results = [
        {
            "error_percentage": 0,
            "cosine_distance": 0.123456789
        },
        {
            "error_percentage": 50,
            "cosine_distance": 0.987654321
        }
    ]

    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_statistical_analysis(results)
        output = fake_out.getvalue()

    # Verify number formatting (6 decimal places)
    assert "0.123457" in output  # rounded to 6 decimals
    assert "0.987654" in output  # rounded to 6 decimals
    # Verify percentage formatting (2 decimal places)
    assert ".00%" in output
