#!/usr/bin/env python3
"""
Error Injector - Injects spelling errors into test sentences

This script takes sentences and creates variations with increasing percentages
of spelling errors by randomly misspelling words.

Usage:
    python src/error_injector.py --input data/test_sentences.json \
      --error-rates 0 10 20 30 40 50 --output data/test_sentences_with_errors/
"""

import json
import argparse
import random
import os
from pathlib import Path
from typing import List, Tuple, Dict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def introduce_typo(word: str) -> str:
    """
    Introduce a single character typo in a word.

    Strategies:
    1. Swap two adjacent characters
    2. Replace a character with a random one
    3. Delete a character
    4. Duplicate a character

    Args:
        word: The word to introduce typo in

    Returns:
        Word with a single character error
    """
    if len(word) < 2:
        return word

    strategies = [
        lambda w: swap_adjacent(w),
        lambda w: replace_char(w),
        lambda w: delete_char(w),
        lambda w: duplicate_char(w),
    ]

    strategy = random.choice(strategies)
    return strategy(word)


def swap_adjacent(word: str) -> str:
    """Swap two adjacent characters."""
    if len(word) < 2:
        return word
    idx = random.randint(0, len(word) - 2)
    word_list = list(word)
    word_list[idx], word_list[idx + 1] = word_list[idx + 1], word_list[idx]
    return ''.join(word_list)


def replace_char(word: str) -> str:
    """Replace a character with a random one."""
    if len(word) == 0:
        return word
    idx = random.randint(0, len(word) - 1)
    replacement = chr(random.randint(ord('a'), ord('z')))
    word_list = list(word)
    word_list[idx] = replacement
    return ''.join(word_list)


def delete_char(word: str) -> str:
    """Delete a character."""
    if len(word) <= 1:
        return word
    idx = random.randint(0, len(word) - 1)
    return word[:idx] + word[idx + 1:]


def duplicate_char(word: str) -> str:
    """Duplicate a character."""
    if len(word) == 0:
        return word
    idx = random.randint(0, len(word) - 1)
    return word[:idx + 1] + word[idx] + word[idx + 1:]


def inject_errors(sentence: str, error_rate: float) -> str:
    """
    Inject spelling errors into a sentence at specified rate.

    Args:
        sentence: The original sentence
        error_rate: Percentage of words to introduce errors (0-100)

    Returns:
        Sentence with spelling errors injected
    """
    if error_rate < 0 or error_rate > 100:
        raise ValueError(f"Error rate must be between 0 and 100, got {error_rate}")

    if error_rate == 0:
        return sentence

    # Split into words, preserving punctuation
    words = sentence.split()
    num_errors = max(1, int(len(words) * error_rate / 100))

    # Randomly select which words to introduce errors in
    error_indices = random.sample(range(len(words)), min(num_errors, len(words)))

    # Introduce errors
    for idx in error_indices:
        word = words[idx]

        # Separate word from trailing punctuation
        trailing_punct = ""
        while word and word[-1] in ".,!?;:":
            trailing_punct = word[-1] + trailing_punct
            word = word[:-1]

        # Introduce typo if word has alphabetic characters
        if any(c.isalpha() for c in word):
            word_with_error = introduce_typo(word.lower())
            words[idx] = word_with_error + trailing_punct

    return ' '.join(words)


def load_sentences(filepath: str) -> List[str]:
    """Load sentences from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sentences = []
    for item in data.get('sentences', []):
        if isinstance(item, dict):
            sentences.append(item.get('original', ''))
        elif isinstance(item, str):
            sentences.append(item)

    return [s for s in sentences if s.strip()]


def save_results(
    error_rate: int,
    original_sentence: str,
    error_sentence: str,
    output_dir: str
) -> None:
    """Save results to file."""
    output_path = Path(output_dir) / f"{error_rate}_percent.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Error Rate: {error_rate}%\n")
        f.write(f"Original: {original_sentence}\n")
        f.write(f"With Errors: {error_sentence}\n")

    logger.info(f"Saved {error_rate}% error rate to {output_path}")


def save_json_results(
    error_rate: int,
    original_sentence: str,
    error_sentence: str,
    word_count: int,
    error_count: int,
    output_dir: str
) -> None:
    """Save results in JSON format."""
    output_path = Path(output_dir) / f"{error_rate}_percent.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "error_rate_percent": error_rate,
        "original_sentence": original_sentence,
        "sentence_with_errors": error_sentence,
        "total_words": word_count,
        "words_with_errors": error_count,
        "actual_error_rate": round((error_count / word_count * 100), 1) if word_count > 0 else 0
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Inject spelling errors into test sentences'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input JSON file with test sentences'
    )
    parser.add_argument(
        '--error-rates',
        nargs='+',
        type=int,
        default=[0, 10, 20, 30, 40, 50],
        help='Error rates to test (e.g., 0 10 20 30 40 50)'
    )
    parser.add_argument(
        '--output',
        default='data/test_sentences_with_errors/',
        help='Output directory for results'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    parser.add_argument(
        '--format',
        choices=['txt', 'json', 'both'],
        default='both',
        help='Output format'
    )

    args = parser.parse_args()

    # Set random seed for reproducibility
    random.seed(args.seed)

    # Load sentences
    logger.info(f"Loading sentences from {args.input}")
    sentences = load_sentences(args.input)

    if not sentences:
        logger.error("No sentences loaded")
        return

    logger.info(f"Loaded {len(sentences)} sentence(s)")

    # For each sentence and error rate
    for sentence in sentences:
        original_words = sentence.split()
        logger.info(f"Processing sentence: {sentence[:50]}... ({len(original_words)} words)")

        for error_rate in args.error_rates:
            # Generate sentence with errors
            error_sentence = inject_errors(sentence, error_rate)

            # Count actual errors
            original_tokens = sentence.split()
            error_tokens = error_sentence.split()
            errors = sum(1 for o, e in zip(original_tokens, error_tokens) if o != e)

            logger.info(
                f"  {error_rate}% errors: {errors}/{len(original_tokens)} words "
                f"({errors/len(original_tokens)*100:.1f}% actual)"
            )

            # Save results
            if args.format in ['txt', 'both']:
                save_results(
                    error_rate,
                    sentence,
                    error_sentence,
                    args.output
                )

            if args.format in ['json', 'both']:
                save_json_results(
                    error_rate,
                    sentence,
                    error_sentence,
                    len(original_tokens),
                    errors,
                    args.output
                )

    logger.info(f"Completed! Results saved to {args.output}")


if __name__ == '__main__':
    main()
