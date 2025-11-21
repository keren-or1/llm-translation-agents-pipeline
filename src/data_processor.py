#!/usr/bin/env python3
"""
Data Processing Module
Handles experiment data loading, processing, and result formatting
"""

import json
import pandas as pd
from typing import List, Dict
from pathlib import Path


def get_default_experiments() -> List[Dict]:
    """
    Return default hardcoded experiments for backward compatibility.

    These experiments contain English sentences with varying error percentages
    (0%, 10%, 20%, 30%, 40%, 50%) and their corresponding final translations.

    Returns:
        List[Dict]: List of experiment dictionaries containing error_percentage,
                    original_english, and final_english fields
    """
    return [
        {
            "error_percentage": 0,
            "original_english": "The advanced artificial intelligence system successfully translates complex linguistic patterns across multiple languages with remarkable accuracy and precision.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models into multiple languages with exceptional accuracy and precision."
        },
        {
            "error_percentage": 10,
            "original_english": "The advansed artificial inteligence system sucessfully translates complex linguistic patterns across multiple languages with remarkable accuracy and precision.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models into multiple languages with exceptional accuracy and precision."
        },
        {
            "error_percentage": 20,
            "original_english": "The advansed artificial inteligence sistem sucessfully translates complex lingustic patterns across multiple languages with remarkable accuracy and precision.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models into multiple languages with exceptional accuracy and precision."
        },
        {
            "error_percentage": 30,
            "original_english": "The advansed artificial inteligence sistem sucessfully translates complex lingustic patterns across multiple langages with remarkble accuracy and precision.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models in multiple languages with exceptional accuracy and precision."
        },
        {
            "error_percentage": 40,
            "original_english": "The advansed articial inteligence sistem sucessfully transltes complex lingustic patterns acros multiple langages with remarkble accuracy and presicion.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models across multiple languages with exceptional accuracy and reliability."
        },
        {
            "error_percentage": 50,
            "original_english": "The advansed articial inteligence sistem sucsessfully transltes complx lingustic patters acros multple langages with remarkble acuracy and presicion.",
            "final_english": "The advanced artificial intelligence system successfully translates complex linguistic models between multiple languages with exceptional accuracy and reliability."
        }
    ]


def load_experiments(input_file: str) -> List[Dict]:
    """
    Load experiments from JSON file with error handling.

    Args:
        input_file (str): Path to JSON file containing experiments

    Returns:
        List[Dict]: List of experiment dictionaries, or None if loading failed

    Note:
        Supports both direct list format and wrapped format with 'experiments' key
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Support both direct list and wrapped format
        if isinstance(data, list):
            experiments = data
        elif isinstance(data, dict) and 'experiments' in data:
            experiments = data['experiments']
        else:
            print(f"Error: Input file must contain 'experiments' list")
            return None

        print(f"✓ Loaded {len(experiments)} experiments from {input_file}\n")
        return experiments
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{input_file}'")
        return None


def create_results_table(results: List[Dict]) -> pd.DataFrame:
    """
    Create a formatted pandas DataFrame from experiment results.

    Args:
        results (List[Dict]): List of result dictionaries containing error_percentage,
                             original_english, final_english, cosine_distance, and
                             cosine_similarity

    Returns:
        pd.DataFrame: Formatted table with truncated text and formatted metrics
    """
    columns = ["Error %", "Original English", "Final English", "Cosine Distance", "Cosine Similarity"]

    if not results:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame([
        {
            "Error %": r["error_percentage"],
            "Original English": r["original_english"][:50] + "...",
            "Final English": r["final_english"][:50] + "...",
            "Cosine Distance": f"{r['cosine_distance']:.6f}",
            "Cosine Similarity": f"{r['cosine_similarity']:.6f}"
        }
        for r in results
    ])
    return df
