"""
Unit Tests for Distance Calculator

Tests cosine distance and similarity calculations.
"""

import pytest
import numpy as np
from src.calculate_results import ExperimentResultsCalculator


class TestDistanceCalculation:
    """Test suite for distance metric calculations."""

    @pytest.fixture
    def calculator(self):
        """Create a calculator instance for testing."""
        return ExperimentResultsCalculator(cache_dir=".test_cache")

    def test_identical_vectors_zero_distance(self, calculator):
        """Test that identical vectors have zero distance."""
        vector = np.array([1.0, 0.0, 0.0])
        distance, similarity = calculator.calculate_cosine_distance(vector, vector)

        assert similarity == pytest.approx(1.0, abs=1e-6)
        assert distance == pytest.approx(0.0, abs=1e-6)

    def test_opposite_vectors_max_distance(self, calculator):
        """Test that opposite vectors have maximum distance."""
        vector1 = np.array([1.0, 0.0, 0.0])
        vector2 = np.array([-1.0, 0.0, 0.0])
        distance, similarity = calculator.calculate_cosine_distance(vector1, vector2)

        assert similarity == pytest.approx(-1.0, abs=1e-6)
        assert distance == pytest.approx(2.0, abs=1e-6)

    def test_orthogonal_vectors_half_distance(self, calculator):
        """Test that orthogonal vectors have 0.5 similarity."""
        vector1 = np.array([1.0, 0.0, 0.0])
        vector2 = np.array([0.0, 1.0, 0.0])
        distance, similarity = calculator.calculate_cosine_distance(vector1, vector2)

        assert similarity == pytest.approx(0.0, abs=1e-6)
        assert distance == pytest.approx(1.0, abs=1e-6)

    def test_distance_similarity_relationship(self, calculator):
        """Test that distance = 1 - similarity."""
        vector1 = np.random.randn(384)  # Random vector
        vector2 = np.random.randn(384)

        distance, similarity = calculator.calculate_cosine_distance(vector1, vector2)

        expected_distance = 1 - similarity
        assert distance == pytest.approx(expected_distance, abs=1e-6)

    def test_symmetric_distance(self, calculator):
        """Test that distance(a, b) == distance(b, a)."""
        vector1 = np.random.randn(384)
        vector2 = np.random.randn(384)

        distance1, similarity1 = calculator.calculate_cosine_distance(vector1, vector2)
        distance2, similarity2 = calculator.calculate_cosine_distance(vector2, vector1)

        assert distance1 == pytest.approx(distance2, abs=1e-6)
        assert similarity1 == pytest.approx(similarity2, abs=1e-6)

    def test_scalar_vectors(self, calculator):
        """Test with single-element vectors."""
        vector1 = np.array([1.0])
        vector2 = np.array([1.0])
        distance, similarity = calculator.calculate_cosine_distance(vector1, vector2)

        assert similarity == pytest.approx(1.0, abs=1e-6)
        assert distance == pytest.approx(0.0, abs=1e-6)

    def test_large_vectors(self, calculator):
        """Test with high-dimensional vectors."""
        vector1 = np.random.randn(1000)
        vector2 = np.random.randn(1000)
        distance, similarity = calculator.calculate_cosine_distance(vector1, vector2)

        # Should be valid numbers in expected range
        assert -1 <= similarity <= 1
        assert 0 <= distance <= 2

    def test_normalized_vectors(self, calculator):
        """Test with normalized vectors."""
        vector1 = np.array([1.0, 0.0, 0.0])  # Already normalized
        vector2 = np.array([0.707, 0.707, 0.0])  # Approximately normalized
        distance, similarity = calculator.calculate_cosine_distance(vector1, vector2)

        # Should give valid cosine similarity
        assert -1 <= similarity <= 1
        assert 0 <= distance <= 2

    def test_return_types(self, calculator):
        """Test that return values are floats."""
        vector1 = np.random.randn(384)
        vector2 = np.random.randn(384)
        distance, similarity = calculator.calculate_cosine_distance(vector1, vector2)

        assert isinstance(distance, float)
        assert isinstance(similarity, float)


class TestExperimentProcessing:
    """Test suite for processing experiments."""

    @pytest.fixture
    def calculator(self):
        """Create a calculator instance for testing."""
        return ExperimentResultsCalculator(cache_dir=".test_cache")

    @pytest.fixture
    def sample_experiments(self):
        """Create sample experiment data."""
        return [
            {
                "error_percentage": 0,
                "original_english": "The test sentence",
                "final_english": "The test sentence"
            },
            {
                "error_percentage": 10,
                "original_english": "The test sentence",
                "final_english": "The tst sentance"  # With errors
            }
        ]

    def test_process_experiments_returns_list(self, calculator, sample_experiments):
        """Test that processing returns a list of results."""
        results = calculator.process_all_experiments(sample_experiments)

        assert isinstance(results, list)
        assert len(results) == len(sample_experiments)

    def test_process_experiments_has_required_fields(self, calculator, sample_experiments):
        """Test that results have all required fields."""
        results = calculator.process_all_experiments(sample_experiments)

        required_fields = {"error_percentage", "cosine_distance", "cosine_similarity", "original_english", "final_english"}
        for result in results:
            assert all(field in result for field in required_fields)

    def test_process_experiments_distances_valid(self, calculator, sample_experiments):
        """Test that distances are in valid range."""
        results = calculator.process_all_experiments(sample_experiments)

        for result in results:
            assert 0 <= result["cosine_distance"] <= 2
            assert -1 <= result["cosine_similarity"] <= 1

    def test_identical_sentences_low_distance(self, calculator):
        """Test that identical sentences have low distance."""
        experiments = [{
            "error_percentage": 0,
            "original_english": "The same sentence",
            "final_english": "The same sentence"
        }]
        results = calculator.process_all_experiments(experiments)

        # Same sentence should have very low distance
        assert results[0]["cosine_distance"] < 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
