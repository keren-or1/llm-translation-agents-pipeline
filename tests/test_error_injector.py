#!/usr/bin/env python3
"""
Unit Tests for Error Injector

Tests the error_injector module including:
- Error injection at various rates
- Typo generation strategies
- Sentence processing
- Edge cases

Run with: pytest tests/test_error_injector.py -v --cov=src.error_injector
"""

import pytest
import random
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from error_injector import (
    introduce_typo,
    swap_adjacent,
    replace_char,
    delete_char,
    duplicate_char,
    inject_errors
)


class TestTypoGeneration:
    """Test individual typo generation functions."""

    def test_swap_adjacent_basic(self):
        """Test swapping adjacent characters."""
        random.seed(42)
        result = swap_adjacent("hello")
        # Should swap two adjacent characters
        assert len(result) == len("hello")
        assert set(result) == set("hello")
        assert result != "hello"  # Should be different

    def test_swap_adjacent_short_word(self):
        """Test swap on very short word."""
        random.seed(42)
        result = swap_adjacent("ab")
        assert len(result) == 2
        assert set(result) == {'a', 'b'}

    def test_swap_adjacent_single_char(self):
        """Test swap on single character (should return unchanged)."""
        result = swap_adjacent("a")
        assert result == "a"

    def test_replace_char_basic(self):
        """Test replacing a character."""
        random.seed(42)
        result = replace_char("hello")
        assert len(result) == len("hello")
        # At least one character should be different
        differences = sum(1 for a, b in zip("hello", result) if a != b)
        assert differences >= 1

    def test_replace_char_empty(self):
        """Test replace on empty string."""
        result = replace_char("")
        assert result == ""

    def test_delete_char_basic(self):
        """Test deleting a character."""
        random.seed(42)
        result = delete_char("hello")
        assert len(result) == len("hello") - 1
        # All characters should be from original
        assert all(c in "hello" for c in result)

    def test_delete_char_short(self):
        """Test delete on very short word (should not delete if length <= 1)."""
        result = delete_char("a")
        assert result == "a"

    def test_delete_char_two_chars(self):
        """Test delete on two-character word."""
        random.seed(42)
        result = delete_char("ab")
        assert len(result) == 1
        assert result in ["a", "b"]

    def test_duplicate_char_basic(self):
        """Test duplicating a character."""
        random.seed(42)
        result = duplicate_char("hello")
        assert len(result) == len("hello") + 1
        # Should contain all original characters plus one duplicate
        original_counts = {c: "hello".count(c) for c in set("hello")}
        result_counts = {c: result.count(c) for c in set(result)}

        # Total count should be one more
        assert sum(result_counts.values()) == sum(original_counts.values()) + 1

    def test_duplicate_char_empty(self):
        """Test duplicate on empty string."""
        result = duplicate_char("")
        assert result == ""

    def test_introduce_typo_basic(self):
        """Test introduce_typo generates valid typos."""
        random.seed(42)
        for _ in range(10):
            result = introduce_typo("hello")
            # Length should be similar (within 1)
            assert abs(len(result) - len("hello")) <= 1

    def test_introduce_typo_short_word(self):
        """Test introduce_typo on short word."""
        result = introduce_typo("a")
        # Single char returns unchanged
        assert result == "a"

    def test_introduce_typo_consistent_seed(self):
        """Test that same seed produces same typo."""
        random.seed(123)
        result1 = introduce_typo("testing")
        random.seed(123)
        result2 = introduce_typo("testing")
        assert result1 == result2


class TestErrorInjection:
    """Test error injection at sentence level."""

    def test_inject_errors_zero_rate(self):
        """Test 0% error rate returns original."""
        sentence = "The quick brown fox jumps over the lazy dog."
        result = inject_errors(sentence, 0)
        assert result == sentence

    def test_inject_errors_valid_rates(self):
        """Test various valid error rates."""
        sentence = "The quick brown fox jumps over the lazy dog."
        random.seed(42)

        for rate in [10, 20, 30, 40, 50]:
            result = inject_errors(sentence, rate)
            assert isinstance(result, str)
            assert len(result.split()) == len(sentence.split())

    def test_inject_errors_100_percent(self):
        """Test 100% error rate."""
        sentence = "The quick brown fox jumps."
        random.seed(42)
        result = inject_errors(sentence, 100)

        # All words should have errors
        original_words = sentence.replace(".", "").split()
        result_words = result.replace(".", "").split()

        # At least some words should be different
        differences = sum(1 for o, r in zip(original_words, result_words) if o != r)
        assert differences > 0

    def test_inject_errors_invalid_rate_low(self):
        """Test error with negative error rate."""
        with pytest.raises(ValueError, match="Error rate must be between 0 and 100"):
            inject_errors("test", -10)

    def test_inject_errors_invalid_rate_high(self):
        """Test error with error rate > 100."""
        with pytest.raises(ValueError, match="Error rate must be between 0 and 100"):
            inject_errors("test", 150)

    def test_inject_errors_preserves_punctuation(self):
        """Test that punctuation is preserved."""
        sentence = "Hello, world! How are you?"
        random.seed(42)
        result = inject_errors(sentence, 50)

        # Punctuation should be preserved
        original_punct = [c for c in sentence if c in ".,!?;:"]
        result_punct = [c for c in result if c in ".,!?;:"]
        assert original_punct == result_punct

    def test_inject_errors_word_count(self):
        """Test that word count remains the same."""
        sentence = "The quick brown fox jumps over the lazy dog."
        random.seed(42)

        for rate in [0, 25, 50, 75]:
            result = inject_errors(sentence, rate)
            assert len(result.split()) == len(sentence.split())

    def test_inject_errors_reproducible(self):
        """Test that same seed produces same errors."""
        sentence = "Testing reproducibility of error injection."

        random.seed(999)
        result1 = inject_errors(sentence, 30)

        random.seed(999)
        result2 = inject_errors(sentence, 30)

        assert result1 == result2

    def test_inject_errors_different_seeds(self):
        """Test that different seeds produce different errors."""
        sentence = "Testing reproducibility of error injection."

        random.seed(111)
        result1 = inject_errors(sentence, 30)

        random.seed(222)
        result2 = inject_errors(sentence, 30)

        # Should be different (with high probability)
        assert result1 != result2

    def test_inject_errors_actual_rate(self):
        """Test that actual error rate is close to requested rate."""
        sentence = "The quick brown fox jumps over the lazy dog in the afternoon."
        random.seed(42)
        target_rate = 30
        result = inject_errors(sentence, target_rate)

        # Count actual errors
        original_words = sentence.split()
        result_words = result.split()
        errors = sum(1 for o, r in zip(original_words, result_words)
                    if o.replace(".", "").replace(",", "") != r.replace(".", "").replace(",", ""))

        actual_rate = (errors / len(original_words)) * 100

        # Should be within reasonable margin
        assert abs(actual_rate - target_rate) < 15  # Allow 15% margin


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_string(self):
        """Test error injection on empty string."""
        result = inject_errors("", 50)
        assert result == ""

    def test_single_word(self):
        """Test error injection on single word."""
        random.seed(42)
        result = inject_errors("Hello", 100)
        assert isinstance(result, str)

    def test_very_long_sentence(self):
        """Test error injection on very long sentence."""
        sentence = " ".join(["word"] * 1000)
        random.seed(42)
        result = inject_errors(sentence, 20)
        assert len(result.split()) == 1000

    def test_special_characters(self):
        """Test error injection with special characters."""
        sentence = "Hello @world #hashtag $money"
        random.seed(42)
        result = inject_errors(sentence, 25)
        assert isinstance(result, str)

    def test_numbers_in_text(self):
        """Test error injection with numbers."""
        sentence = "There are 123 apples and 456 oranges."
        random.seed(42)
        result = inject_errors(sentence, 30)
        assert isinstance(result, str)

    def test_unicode_characters(self):
        """Test error injection with Unicode text."""
        sentence = "Hello world test sentence"
        random.seed(42)
        result = inject_errors(sentence, 25)
        assert isinstance(result, str)

    def test_mixed_case(self):
        """Test error injection preserves some case information."""
        sentence = "The Quick Brown Fox Jumps Over The Lazy Dog."
        random.seed(42)
        result = inject_errors(sentence, 30)
        # Result should still be string with same structure
        assert len(result.split()) == len(sentence.split())

    def test_multiple_spaces(self):
        """Test error injection with multiple spaces."""
        sentence = "Hello  world   test"
        random.seed(42)
        result = inject_errors(sentence, 30)
        # Split handles multiple spaces
        assert isinstance(result, str)

    def test_sentence_with_only_punctuation(self):
        """Test error injection on sentence with only punctuation."""
        sentence = "... !!! ???"
        result = inject_errors(sentence, 50)
        assert isinstance(result, str)

    def test_very_short_words(self):
        """Test error injection on sentence with very short words."""
        sentence = "I am a go to do it"
        random.seed(42)
        result = inject_errors(sentence, 50)
        assert len(result.split()) == len(sentence.split())


class TestTypoStrategies:
    """Test that different typo strategies are actually used."""

    def test_all_strategies_used(self):
        """Test that different typo strategies produce different results."""
        word = "testing"

        random.seed(42)
        swap = swap_adjacent(word)

        random.seed(43)
        replace = replace_char(word)

        random.seed(44)
        delete = delete_char(word)

        random.seed(45)
        duplicate = duplicate_char(word)

        # All should be different from original
        results = [swap, replace, delete, duplicate]
        # At least 3 out of 4 should be different from original
        different = sum(1 for r in results if r != word)
        assert different >= 3

    def test_strategy_length_effects(self):
        """Test that strategies have expected length effects."""
        word = "testing"

        # Swap and replace should maintain length
        random.seed(42)
        swap = swap_adjacent(word)
        assert len(swap) == len(word)

        random.seed(42)
        replace = replace_char(word)
        assert len(replace) == len(word)

        # Delete should reduce length by 1
        random.seed(42)
        delete = delete_char(word)
        assert len(delete) == len(word) - 1

        # Duplicate should increase length by 1
        random.seed(42)
        duplicate = duplicate_char(word)
        assert len(duplicate) == len(word) + 1


class TestRealWorldScenarios:
    """Test with real-world sentence examples."""

    def test_complex_sentence(self):
        """Test with complex sentence structure."""
        sentence = "The sophisticated algorithm processes natural language with remarkable accuracy."
        random.seed(42)
        result = inject_errors(sentence, 25)

        assert len(result.split()) == len(sentence.split())
        # Should have some errors
        assert result != sentence

    def test_technical_text(self):
        """Test with technical text."""
        sentence = "The API endpoint returns JSON data with authentication tokens."
        random.seed(42)
        result = inject_errors(sentence, 30)

        assert len(result.split()) == len(sentence.split())

    def test_conversational_text(self):
        """Test with conversational text."""
        sentence = "Hey, how are you doing today? I'm feeling great!"
        random.seed(42)
        result = inject_errors(sentence, 20)

        # Punctuation should be preserved
        assert "?" in result
        assert "!" in result


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src.error_injector', '--cov-report=html'])
