"""
Unit tests for data_processor module
"""

import pytest
import json
import sys
from pathlib import Path
import tempfile
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_processor import get_default_experiments, load_experiments, create_results_table


def test_get_default_experiments():
    """Test that default experiments are returned correctly"""
    experiments = get_default_experiments()

    assert isinstance(experiments, list)
    assert len(experiments) == 6  # 0%, 10%, 20%, 30%, 40%, 50%

    # Check structure of first experiment
    exp = experiments[0]
    assert "error_percentage" in exp
    assert "original_english" in exp
    assert "final_english" in exp

    # Check error percentages are correct
    error_pcts = [e["error_percentage"] for e in experiments]
    assert error_pcts == [0, 10, 20, 30, 40, 50]

    # Check all texts are non-empty strings
    for exp in experiments:
        assert isinstance(exp["original_english"], str)
        assert isinstance(exp["final_english"], str)
        assert len(exp["original_english"]) > 0
        assert len(exp["final_english"]) > 0


def test_load_experiments_valid_file():
    """Test loading experiments from valid JSON file"""
    # Create temporary JSON file
    test_data = {
        "experiments": [
            {
                "error_percentage": 0,
                "original_english": "Test sentence",
                "final_english": "Test result"
            },
            {
                "error_percentage": 10,
                "original_english": "Anothr test sentance",
                "final_english": "Another test result"
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    try:
        experiments = load_experiments(temp_file)

        assert experiments is not None
        assert len(experiments) == 2
        assert experiments[0]["error_percentage"] == 0
        assert experiments[1]["error_percentage"] == 10
    finally:
        Path(temp_file).unlink()


def test_load_experiments_direct_list():
    """Test loading experiments from JSON file with direct list format"""
    # Create temporary JSON file with direct list (no wrapper)
    test_data = [
        {
            "error_percentage": 5,
            "original_english": "Direct list test",
            "final_english": "Direct list result"
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    try:
        experiments = load_experiments(temp_file)

        assert experiments is not None
        assert len(experiments) == 1
        assert experiments[0]["error_percentage"] == 5
    finally:
        Path(temp_file).unlink()


def test_load_experiments_file_not_found():
    """Test loading from non-existent file returns None"""
    experiments = load_experiments("nonexistent_file.json")
    assert experiments is None


def test_load_experiments_invalid_json():
    """Test loading invalid JSON returns None"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json content")
        temp_file = f.name

    try:
        experiments = load_experiments(temp_file)
        assert experiments is None
    finally:
        Path(temp_file).unlink()


def test_load_experiments_wrong_structure():
    """Test loading JSON with wrong structure returns None"""
    test_data = {"wrong_key": [{"data": "value"}]}

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    try:
        experiments = load_experiments(temp_file)
        assert experiments is None
    finally:
        Path(temp_file).unlink()


def test_create_results_table():
    """Test creating results table from experiment results"""
    results = [
        {
            "error_percentage": 0,
            "original_english": "This is a long sentence that should be truncated in the table display because it exceeds fifty characters",
            "final_english": "This is also a long sentence that should be truncated for table display purposes",
            "cosine_distance": 0.123456,
            "cosine_similarity": 0.876544
        },
        {
            "error_percentage": 10,
            "original_english": "Short sentence",
            "final_english": "Short result",
            "cosine_distance": 0.234567,
            "cosine_similarity": 0.765433
        }
    ]

    df = create_results_table(results)

    # Check DataFrame structure
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["Error %", "Original English", "Final English", "Cosine Distance", "Cosine Similarity"]

    # Check data types and values
    assert df["Error %"].iloc[0] == 0
    assert df["Error %"].iloc[1] == 10

    # Check truncation (should be 50 chars + "...")
    assert len(df["Original English"].iloc[0]) == 53  # 50 + "..."
    assert df["Original English"].iloc[0].endswith("...")

    # Short sentence should also have "..." appended
    assert df["Original English"].iloc[1] == "Short sentence..."

    # Check distance formatting (6 decimal places)
    assert df["Cosine Distance"].iloc[0] == "0.123456"
    assert df["Cosine Similarity"].iloc[1] == "0.765433"


def test_create_results_table_empty():
    """Test creating table from empty results"""
    results = []
    df = create_results_table(results)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert list(df.columns) == ["Error %", "Original English", "Final English", "Cosine Distance", "Cosine Similarity"]


def test_experiments_data_consistency():
    """Test that default experiments have consistent word counts"""
    experiments = get_default_experiments()

    # All original_english should have similar word counts (within reason)
    word_counts = [len(exp["original_english"].split()) for exp in experiments]

    # Should all be around 15-20 words (assignment requirement >= 15)
    assert all(count >= 15 for count in word_counts)

    # Variance should be small (same base sentence with errors)
    assert max(word_counts) - min(word_counts) <= 5
