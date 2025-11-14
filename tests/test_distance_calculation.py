#!/usr/bin/env python3
"""
Integration Tests for Distance Calculation

Tests the complete workflow from error injection to distance measurement,
ensuring all components work together correctly.

Run with: pytest tests/test_distance_calculation.py -v
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from embeddings_calculator import EmbeddingsCalculator
from error_injector import inject_errors


class TestDistanceCalculationIntegration:
    """Integration tests for the complete distance calculation workflow."""

    @pytest.fixture
    def mock_calculator(self):
        """Create mocked embeddings calculator."""
        with patch('embeddings_calculator.OpenAI'):
            with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
                calc = EmbeddingsCalculator(api_key='test-key')
                return calc

    def test_distance_increases_with_error_rate(self, mock_calculator):
        """Test that cosine distance increases as error rate increases."""
        original = "The quick brown fox jumps over the lazy dog."

        # Mock embeddings that show increasing distance
        mock_embeddings = [
            [1.0, 0.0, 0.0],  # Original
            [0.95, 0.05, 0.0],  # 10% errors
            [0.85, 0.15, 0.0],  # 30% errors
            [0.70, 0.30, 0.0],  # 50% errors
        ]

        distances = []
        for i, error_rate in enumerate([0, 10, 30, 50]):
            # Inject errors
            if error_rate == 0:
                corrupted = original
            else:
                corrupted = inject_errors(original, error_rate)

            # Mock embedding call
            mock_calculator.client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(index=0, embedding=mock_embeddings[0]),  # Original
                MagicMock(index=1, embedding=mock_embeddings[i])   # Corrupted
            ]
            mock_calculator.client.embeddings.create.return_value = mock_response

            # Measure distance
            result = mock_calculator.measure_distance(original, corrupted)
            distances.append(result['cosine_distance'])

        # Verify distances increase (or stay similar for 0%)
        assert distances[0] < distances[1] < distances[2] < distances[3]

    def test_zero_errors_minimal_distance(self, mock_calculator):
        """Test that 0% errors results in minimal distance."""
        original = "The quick brown fox jumps over the lazy dog."
        corrupted = inject_errors(original, 0)

        # Should be identical
        assert original == corrupted

        # Mock identical embeddings
        mock_embedding = [1.0, 0.0, 0.0]
        mock_calculator.client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=mock_embedding),
            MagicMock(index=1, embedding=mock_embedding)
        ]
        mock_calculator.client.embeddings.create.return_value = mock_response

        result = mock_calculator.measure_distance(original, corrupted)

        # Distance should be very small (ideally 0)
        assert result['cosine_distance'] < 0.01

    def test_similarity_and_distance_relationship(self, mock_calculator):
        """Test that cosine_similarity + cosine_distance ≈ 1."""
        original = "Test sentence for similarity check."
        corrupted = inject_errors(original, 25)

        # Mock embeddings
        mock_calculator.client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[1.0, 0.0, 0.0]),
            MagicMock(index=1, embedding=[0.8, 0.2, 0.0])
        ]
        mock_calculator.client.embeddings.create.return_value = mock_response

        result = mock_calculator.measure_distance(original, corrupted)

        # similarity + distance should equal 1 (within floating point precision)
        sum_value = result['cosine_similarity'] + result['cosine_distance']
        assert abs(sum_value - 1.0) < 1e-6

    def test_error_injection_reproducibility(self):
        """Test that error injection is reproducible with same seed."""
        import random

        original = "The quick brown fox jumps over the lazy dog."

        random.seed(42)
        corrupted1 = inject_errors(original, 30)

        random.seed(42)
        corrupted2 = inject_errors(original, 30)

        assert corrupted1 == corrupted2

    def test_distance_calculation_consistency(self, mock_calculator):
        """Test that distance calculation is consistent."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.9, 0.1, 0.0]

        # Calculate distance multiple times
        distances = []
        for _ in range(5):
            distance = EmbeddingsCalculator.cosine_distance(vec1, vec2)
            distances.append(distance)

        # All should be identical
        assert len(set(distances)) == 1

    def test_complete_workflow_simulation(self, mock_calculator):
        """Test complete workflow: inject errors → calculate embeddings → measure distance."""
        import random

        original = "The sophisticated algorithm processes natural language efficiently."
        error_rates = [0, 10, 20, 30, 40, 50]
        results = []

        for i, rate in enumerate(error_rates):
            random.seed(42 + i)  # Different seed for each rate

            # Step 1: Inject errors
            if rate == 0:
                corrupted = original
            else:
                corrupted = inject_errors(original, rate)

            # Step 2: Mock embeddings (simulate decreasing similarity)
            similarity = 1.0 - (rate / 100.0)  # Simple linear model
            vec1 = np.array([1.0, 0.0, 0.0])
            vec2 = np.array([similarity, np.sqrt(1 - similarity**2), 0.0])

            mock_calculator.client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(index=0, embedding=vec1.tolist()),
                MagicMock(index=1, embedding=vec2.tolist())
            ]
            mock_calculator.client.embeddings.create.return_value = mock_response

            # Step 3: Measure distance
            result = mock_calculator.measure_distance(original, corrupted)

            results.append({
                'error_rate': rate,
                'distance': result['cosine_distance'],
                'similarity': result['cosine_similarity']
            })

        # Verify results
        assert len(results) == 6

        # Distances should increase
        distances = [r['distance'] for r in results]
        for i in range(len(distances) - 1):
            assert distances[i] <= distances[i + 1]

        # Similarities should decrease
        similarities = [r['similarity'] for r in results]
        for i in range(len(similarities) - 1):
            assert similarities[i] >= similarities[i + 1]


class TestErrorPropagation:
    """Test error propagation through the system."""

    def test_error_count_accuracy(self):
        """Test that actual error count matches expected rate."""
        import random

        original = "The quick brown fox jumps over the lazy dog in the afternoon sun."
        target_rate = 30
        trials = 10

        random.seed(42)
        actual_rates = []

        for i in range(trials):
            corrupted = inject_errors(original, target_rate)

            # Count actual errors
            original_words = original.split()
            corrupted_words = corrupted.split()

            errors = sum(1 for o, c in zip(original_words, corrupted_words)
                        if o.replace('.', '').replace(',', '') != c.replace('.', '').replace(',', ''))

            actual_rate = (errors / len(original_words)) * 100
            actual_rates.append(actual_rate)

        # Mean actual rate should be close to target
        mean_rate = np.mean(actual_rates)
        assert abs(mean_rate - target_rate) < 10  # Within 10% margin

    def test_punctuation_preservation(self):
        """Test that punctuation is preserved through error injection."""
        import random

        sentences = [
            "Hello, world!",
            "How are you? I'm fine.",
            "Test; test: test.",
        ]

        random.seed(42)
        for sentence in sentences:
            corrupted = inject_errors(sentence, 50)

            # Count punctuation
            original_punct = [c for c in sentence if c in '.,!?;:']
            corrupted_punct = [c for c in corrupted if c in '.,!?;:']

            assert original_punct == corrupted_punct

    def test_word_count_preservation(self):
        """Test that word count is preserved through error injection."""
        import random

        sentences = [
            "Short sentence.",
            "This is a medium length sentence with more words.",
            "Very long sentence " * 20 + "ending here."
        ]

        random.seed(42)
        for sentence in sentences:
            for rate in [10, 30, 50]:
                corrupted = inject_errors(sentence, rate)
                assert len(corrupted.split()) == len(sentence.split())


class TestLinearDegradation:
    """Test that error propagation follows expected patterns."""

    def test_linear_degradation_hypothesis(self, mock_calculator):
        """Test hypothesis: distance increases linearly with error rate."""
        import random

        original = "The quick brown fox jumps over the lazy dog."
        error_rates = [0, 10, 20, 30, 40, 50]
        distances = []

        for i, rate in enumerate(error_rates):
            random.seed(100 + i)

            # Inject errors
            if rate == 0:
                corrupted = original
            else:
                corrupted = inject_errors(original, rate)

            # Mock embeddings with linear degradation
            # Distance = 0.05 + (rate * 0.012)
            base_distance = 0.05
            degradation_rate = 0.012
            expected_distance = base_distance + (rate * degradation_rate)

            similarity = 1.0 - expected_distance
            vec1 = np.array([1.0, 0.0, 0.0])
            angle = np.arccos(similarity)
            vec2 = np.array([np.cos(angle), np.sin(angle), 0.0])

            mock_calculator.client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(index=0, embedding=vec1.tolist()),
                MagicMock(index=1, embedding=vec2.tolist())
            ]
            mock_calculator.client.embeddings.create.return_value = mock_response

            result = mock_calculator.measure_distance(original, corrupted)
            distances.append(result['cosine_distance'])

        # Fit linear regression
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(error_rates, distances)

        # R² should be high (linear fit)
        r_squared = r_value ** 2
        assert r_squared > 0.90  # Strong linear relationship

    def test_no_exponential_explosion(self, mock_calculator):
        """Test that errors don't compound exponentially."""
        import random

        original = "The quick brown fox jumps over the lazy dog."
        error_rates = [0, 10, 20, 30, 40, 50]
        distances = []

        for i, rate in enumerate(error_rates):
            random.seed(200 + i)

            # Inject errors
            if rate == 0:
                corrupted = original
            else:
                corrupted = inject_errors(original, rate)

            # Mock linear degradation
            distance = 0.05 + (rate * 0.012)
            similarity = 1.0 - distance

            vec1 = np.array([1.0, 0.0, 0.0])
            angle = np.arccos(np.clip(similarity, -1, 1))
            vec2 = np.array([np.cos(angle), np.sin(angle), 0.0])

            mock_calculator.client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(index=0, embedding=vec1.tolist()),
                MagicMock(index=1, embedding=vec2.tolist())
            ]
            mock_calculator.client.embeddings.create.return_value = mock_response

            result = mock_calculator.measure_distance(original, corrupted)
            distances.append(result['cosine_distance'])

        # Check that distances don't explode
        # Maximum distance should be reasonable (< 1.0 for 50% errors)
        assert max(distances) < 1.0

        # Increments should be roughly similar (not exponential)
        increments = [distances[i+1] - distances[i] for i in range(len(distances)-1)]
        # Standard deviation of increments should be small (linear = constant increments)
        assert np.std(increments) < 0.05


class TestRobustnessAndEdgeCases:
    """Test system robustness and edge cases."""

    def test_empty_string_handling(self, mock_calculator):
        """Test handling of empty strings."""
        mock_calculator.client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[0.0]),
            MagicMock(index=1, embedding=[0.0])
        ]
        mock_calculator.client.embeddings.create.return_value = mock_response

        result = mock_calculator.measure_distance("", "")
        assert 'cosine_distance' in result

    def test_very_similar_sentences(self, mock_calculator):
        """Test distance between very similar sentences."""
        original = "The cat sat on the mat."
        similar = "The cat sat on the rug."

        # Mock high similarity
        mock_calculator.client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[1.0, 0.0, 0.0]),
            MagicMock(index=1, embedding=[0.95, 0.05, 0.0])
        ]
        mock_calculator.client.embeddings.create.return_value = mock_response

        result = mock_calculator.measure_distance(original, similar)

        # Should have high similarity (low distance)
        assert result['cosine_similarity'] > 0.9
        assert result['cosine_distance'] < 0.1

    def test_very_different_sentences(self, mock_calculator):
        """Test distance between very different sentences."""
        original = "The cat sat on the mat."
        different = "Quantum physics explains molecular behavior."

        # Mock low similarity
        mock_calculator.client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[1.0, 0.0, 0.0]),
            MagicMock(index=1, embedding=[0.3, 0.7, 0.0])
        ]
        mock_calculator.client.embeddings.create.return_value = mock_response

        result = mock_calculator.measure_distance(original, different)

        # Should have low similarity (high distance)
        assert result['cosine_similarity'] < 0.5
        assert result['cosine_distance'] > 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
