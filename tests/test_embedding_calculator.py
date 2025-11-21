"""
Unit tests for embedding_calculator module
"""

import pytest
import numpy as np
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from embedding_calculator import EmbeddingCalculator


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def calculator(temp_cache_dir):
    """Create EmbeddingCalculator instance with temporary cache"""
    return EmbeddingCalculator(cache_dir=temp_cache_dir)


def test_embedding_calculator_initialization(temp_cache_dir):
    """Test that EmbeddingCalculator initializes correctly"""
    calc = EmbeddingCalculator(cache_dir=temp_cache_dir)
    assert calc.model is not None
    assert calc.cache_dir.exists()
    assert str(calc.cache_dir) == temp_cache_dir


def test_get_embedding_cache_path(calculator):
    """Test cache path generation uses MD5 hashing"""
    text = "test sentence"
    cache_path = calculator.get_embedding_cache_path(text)

    assert isinstance(cache_path, Path)
    assert cache_path.parent == calculator.cache_dir
    assert cache_path.name.startswith("embedding_")
    assert cache_path.suffix == ".npy"

    # Same text should generate same path
    cache_path2 = calculator.get_embedding_cache_path(text)
    assert cache_path == cache_path2


def test_get_or_calculate_embedding(calculator):
    """Test embedding calculation and caching"""
    text = "This is a test sentence for embedding calculation."

    # First call should calculate and cache
    embedding1 = calculator.get_or_calculate_embedding(text)

    assert isinstance(embedding1, np.ndarray)
    assert len(embedding1.shape) == 1  # 1D array
    assert embedding1.shape[0] == 384  # all-MiniLM-L6-v2 dimension

    # Verify cache file was created
    cache_path = calculator.get_embedding_cache_path(text)
    assert cache_path.exists()

    # Second call should load from cache (same result)
    embedding2 = calculator.get_or_calculate_embedding(text)
    np.testing.assert_array_equal(embedding1, embedding2)


def test_calculate_cosine_distance(calculator):
    """Test cosine distance calculation"""
    # Create two known embeddings
    text1 = "The quick brown fox jumps"
    text2 = "The fast brown fox leaps"
    text3 = "Completely different unrelated content"

    emb1 = calculator.get_or_calculate_embedding(text1)
    emb2 = calculator.get_or_calculate_embedding(text2)
    emb3 = calculator.get_or_calculate_embedding(text3)

    # Calculate distances
    dist_similar, sim_similar = calculator.calculate_cosine_distance(emb1, emb2)
    dist_different, sim_different = calculator.calculate_cosine_distance(emb1, emb3)

    # Similar sentences should have low distance, high similarity
    assert 0 <= dist_similar <= 2
    assert 0 <= sim_similar <= 1
    assert dist_similar + sim_similar == pytest.approx(1.0)

    # Different sentences should have higher distance, lower similarity
    assert dist_different > dist_similar
    assert sim_different < sim_similar

    # Identical embeddings should have distance 0, similarity 1
    dist_identical, sim_identical = calculator.calculate_cosine_distance(emb1, emb1)
    assert dist_identical == pytest.approx(0.0, abs=1e-6)
    assert sim_identical == pytest.approx(1.0, abs=1e-6)


def test_cache_persistence(calculator):
    """Test that cache persists across calculator instances"""
    text = "Test sentence for cache persistence"

    # Calculate with first calculator
    embedding1 = calculator.get_or_calculate_embedding(text)
    cache_path = calculator.get_embedding_cache_path(text)
    assert cache_path.exists()

    # Create new calculator with same cache directory
    calculator2 = EmbeddingCalculator(cache_dir=str(calculator.cache_dir))

    # Should load from cache (not recalculate)
    embedding2 = calculator2.get_or_calculate_embedding(text)
    np.testing.assert_array_equal(embedding1, embedding2)


def test_different_texts_different_embeddings(calculator):
    """Test that different texts produce different embeddings"""
    text1 = "First unique sentence"
    text2 = "Second unique sentence"

    emb1 = calculator.get_or_calculate_embedding(text1)
    emb2 = calculator.get_or_calculate_embedding(text2)

    # Embeddings should be different
    assert not np.array_equal(emb1, emb2)

    # But should have same shape
    assert emb1.shape == emb2.shape
