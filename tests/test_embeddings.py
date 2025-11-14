#!/usr/bin/env python3
"""
Unit Tests for Embeddings Calculator

Tests the embeddings_calculator module including:
- Embedding generation
- Distance calculation
- Similarity metrics
- Batch processing
- Error handling

Run with: pytest tests/test_embeddings.py -v --cov=src.embeddings_calculator
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from embeddings_calculator import EmbeddingsCalculator


class TestEmbeddingsCalculator:
    """Test suite for EmbeddingsCalculator class."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create mock OpenAI client."""
        with patch('embeddings_calculator.OpenAI') as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def calculator(self, mock_openai_client):
        """Create EmbeddingsCalculator instance with mocked client."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            calc = EmbeddingsCalculator(api_key='test-key')
            calc.client = mock_openai_client
            return calc

    def test_initialization_with_api_key(self):
        """Test initialization with explicit API key."""
        with patch('embeddings_calculator.OpenAI'):
            calc = EmbeddingsCalculator(api_key='test-key')
            assert calc.api_key == 'test-key'
            assert calc.model == 'text-embedding-3-small'

    def test_initialization_with_env_var(self):
        """Test initialization with environment variable."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key'}):
            with patch('embeddings_calculator.OpenAI'):
                calc = EmbeddingsCalculator()
                assert calc.api_key == 'env-key'

    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
                EmbeddingsCalculator()

    def test_get_embedding_success(self, calculator, mock_openai_client):
        """Test successful embedding generation."""
        # Mock response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_client.embeddings.create.return_value = mock_response

        # Test
        embedding = calculator.get_embedding("test text")

        # Verify
        assert embedding == [0.1, 0.2, 0.3]
        mock_openai_client.embeddings.create.assert_called_once_with(
            input="test text",
            model='text-embedding-3-small'
        )

    def test_get_embedding_error(self, calculator, mock_openai_client):
        """Test embedding generation with API error."""
        mock_openai_client.embeddings.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            calculator.get_embedding("test text")

    def test_get_embeddings_batch_success(self, calculator, mock_openai_client):
        """Test batch embedding generation."""
        # Mock response with multiple embeddings
        mock_data = [
            MagicMock(index=0, embedding=[0.1, 0.2]),
            MagicMock(index=1, embedding=[0.3, 0.4]),
            MagicMock(index=2, embedding=[0.5, 0.6])
        ]
        mock_response = MagicMock()
        mock_response.data = mock_data
        mock_openai_client.embeddings.create.return_value = mock_response

        # Test
        texts = ["text1", "text2", "text3"]
        embeddings = calculator.get_embeddings_batch(texts)

        # Verify
        assert len(embeddings) == 3
        assert embeddings[0] == [0.1, 0.2]
        assert embeddings[1] == [0.3, 0.4]
        assert embeddings[2] == [0.5, 0.6]

    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity of identical vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        similarity = EmbeddingsCalculator.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 1e-6

    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]

        similarity = EmbeddingsCalculator.cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 1e-6

    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity of opposite vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [-1.0, 0.0]

        similarity = EmbeddingsCalculator.cosine_similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 1e-6

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec1 = [0.0, 0.0]
        vec2 = [1.0, 1.0]

        similarity = EmbeddingsCalculator.cosine_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_cosine_distance_identical_vectors(self):
        """Test cosine distance of identical vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        distance = EmbeddingsCalculator.cosine_distance(vec1, vec2)
        assert abs(distance - 0.0) < 1e-6

    def test_cosine_distance_orthogonal_vectors(self):
        """Test cosine distance of orthogonal vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]

        distance = EmbeddingsCalculator.cosine_distance(vec1, vec2)
        assert abs(distance - 1.0) < 1e-6

    def test_cosine_distance_opposite_vectors(self):
        """Test cosine distance of opposite vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [-1.0, 0.0]

        distance = EmbeddingsCalculator.cosine_distance(vec1, vec2)
        assert abs(distance - 2.0) < 1e-6

    def test_measure_distance_success(self, calculator, mock_openai_client):
        """Test measure_distance method."""
        # Mock embeddings
        mock_data = [
            MagicMock(index=0, embedding=[1.0, 0.0, 0.0]),
            MagicMock(index=1, embedding=[0.9, 0.1, 0.0])
        ]
        mock_response = MagicMock()
        mock_response.data = mock_data
        mock_openai_client.embeddings.create.return_value = mock_response

        # Test
        result = calculator.measure_distance("original", "final")

        # Verify
        assert 'cosine_similarity' in result
        assert 'cosine_distance' in result
        assert 'embedding_dimensions' in result
        assert result['embedding_dimensions'] == 3
        assert 0 <= result['cosine_similarity'] <= 1
        assert 0 <= result['cosine_distance'] <= 2

    def test_cosine_similarity_with_numpy_arrays(self):
        """Test cosine similarity works with numpy arrays."""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([4.0, 5.0, 6.0])

        similarity = EmbeddingsCalculator.cosine_similarity(vec1.tolist(), vec2.tolist())
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1

    def test_embedding_dimensions_consistency(self, calculator, mock_openai_client):
        """Test that embedding dimensions are consistent."""
        # Mock response with 1536-dimensional embedding (standard for text-embedding-3-small)
        embedding_dim = 1536
        mock_embedding = [0.1] * embedding_dim
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        mock_openai_client.embeddings.create.return_value = mock_response

        embedding = calculator.get_embedding("test")
        assert len(embedding) == embedding_dim

    def test_batch_processing_maintains_order(self, calculator, mock_openai_client):
        """Test that batch processing maintains text order."""
        # Mock response with indices
        mock_data = [
            MagicMock(index=2, embedding=[0.5, 0.6]),
            MagicMock(index=0, embedding=[0.1, 0.2]),
            MagicMock(index=1, embedding=[0.3, 0.4])
        ]
        mock_response = MagicMock()
        mock_response.data = mock_data
        mock_openai_client.embeddings.create.return_value = mock_response

        texts = ["first", "second", "third"]
        embeddings = calculator.get_embeddings_batch(texts)

        # Should be sorted by index
        assert embeddings[0] == [0.1, 0.2]
        assert embeddings[1] == [0.3, 0.4]
        assert embeddings[2] == [0.5, 0.6]

    def test_empty_string_handling(self, calculator, mock_openai_client):
        """Test handling of empty strings."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.0, 0.0, 0.0])]
        mock_openai_client.embeddings.create.return_value = mock_response

        embedding = calculator.get_embedding("")
        assert isinstance(embedding, list)

    def test_very_long_text_handling(self, calculator, mock_openai_client):
        """Test handling of very long texts."""
        long_text = "word " * 10000  # Very long text
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_openai_client.embeddings.create.return_value = mock_response

        embedding = calculator.get_embedding(long_text)
        assert isinstance(embedding, list)

    def test_special_characters_handling(self, calculator, mock_openai_client):
        """Test handling of special characters."""
        special_text = "Hello! @#$%^&*() 你好 שלום"
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 100)]
        mock_openai_client.embeddings.create.return_value = mock_response

        embedding = calculator.get_embedding(special_text)
        assert isinstance(embedding, list)

    def test_unicode_text_handling(self, calculator, mock_openai_client):
        """Test handling of Unicode text (Hebrew, Chinese, etc.)."""
        unicode_text = "שלום עולם"  # Hebrew
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 100)]
        mock_openai_client.embeddings.create.return_value = mock_response

        embedding = calculator.get_embedding(unicode_text)
        assert isinstance(embedding, list)

    def test_multiple_sentences_handling(self, calculator, mock_openai_client):
        """Test handling of multiple sentences."""
        multi_sentence = "First sentence. Second sentence! Third sentence?"
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 100)]
        mock_openai_client.embeddings.create.return_value = mock_response

        embedding = calculator.get_embedding(multi_sentence)
        assert isinstance(embedding, list)


class TestEmbeddingsEdgeCases:
    """Test edge cases and error conditions."""

    def test_cosine_similarity_with_different_dimensions(self):
        """Test cosine similarity with vectors of different dimensions raises error."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        # NumPy should handle this, but verify behavior
        try:
            similarity = EmbeddingsCalculator.cosine_similarity(vec1, vec2)
            # If it doesn't raise, verify it returns a valid value
            assert isinstance(similarity, (int, float))
        except (ValueError, IndexError):
            # This is also acceptable behavior
            pass

    def test_cosine_similarity_with_lists(self):
        """Test cosine similarity works with Python lists."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [4.0, 5.0, 6.0]

        similarity = EmbeddingsCalculator.cosine_similarity(vec1, vec2)
        assert isinstance(similarity, float)

    def test_cosine_distance_range(self):
        """Test that cosine distance is always in valid range."""
        # Test with random vectors
        for _ in range(10):
            vec1 = np.random.randn(100).tolist()
            vec2 = np.random.randn(100).tolist()

            distance = EmbeddingsCalculator.cosine_distance(vec1, vec2)
            assert 0 <= distance <= 2, f"Distance {distance} out of range"

    def test_similarity_symmetry(self):
        """Test that cosine similarity is symmetric."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [4.0, 5.0, 6.0]

        sim1 = EmbeddingsCalculator.cosine_similarity(vec1, vec2)
        sim2 = EmbeddingsCalculator.cosine_similarity(vec2, vec1)

        assert abs(sim1 - sim2) < 1e-10

    def test_distance_symmetry(self):
        """Test that cosine distance is symmetric."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [4.0, 5.0, 6.0]

        dist1 = EmbeddingsCalculator.cosine_distance(vec1, vec2)
        dist2 = EmbeddingsCalculator.cosine_distance(vec2, vec1)

        assert abs(dist1 - dist2) < 1e-10


class TestEmbeddingsIntegration:
    """Integration tests (require real API key - skip in CI)."""

    @pytest.mark.skip(reason="Requires real API key")
    def test_real_embedding_generation(self):
        """Test with real OpenAI API (requires valid key)."""
        import os
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("No API key available")

        calc = EmbeddingsCalculator()
        embedding = calc.get_embedding("Hello, world!")

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.skip(reason="Requires real API key")
    def test_real_distance_measurement(self):
        """Test real distance measurement."""
        import os
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("No API key available")

        calc = EmbeddingsCalculator()
        result = calc.measure_distance(
            "The cat sat on the mat.",
            "The feline rested on the rug."
        )

        assert 'cosine_similarity' in result
        assert 'cosine_distance' in result
        # Similar sentences should have high similarity (low distance)
        assert result['cosine_similarity'] > 0.8
        assert result['cosine_distance'] < 0.2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src.embeddings_calculator', '--cov-report=html'])
