"""
Configuration Management Module

Centralized configuration for the Translation Agents Pipeline.
Supports loading from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Configuration class for the Translation Agents Pipeline."""

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    SRC_DIR = Path(__file__).parent
    DOCS_DIR = PROJECT_ROOT / "docs"
    RESULTS_DIR = PROJECT_ROOT / "results"
    SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"

    # Embedding Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION = 384  # Fixed for all-MiniLM-L6-v2

    # Cache Configuration
    CACHE_DIR = os.getenv("CACHE_DIR", str(PROJECT_ROOT / ".cache"))
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"

    # Input/Output File Paths
    DEFAULT_INPUT_FILE = DOCS_DIR / "experiments_input.json"
    DEFAULT_OUTPUT_FILE = DOCS_DIR / "experiment_results.json"
    DEFAULT_MARKDOWN_OUTPUT = DOCS_DIR / "experiment_data.md"
    DEFAULT_GRAPH_OUTPUT = SCREENSHOTS_DIR / "translation_distance_graph.png"

    # Custom paths from environment
    INPUT_FILE = os.getenv("INPUT_FILE", str(DEFAULT_INPUT_FILE))
    OUTPUT_FILE = os.getenv("OUTPUT_FILE", str(DEFAULT_OUTPUT_FILE))
    MARKDOWN_OUTPUT = os.getenv("MARKDOWN_OUTPUT", str(DEFAULT_MARKDOWN_OUTPUT))
    GRAPH_OUTPUT = os.getenv("GRAPH_OUTPUT", str(DEFAULT_GRAPH_OUTPUT))

    # Visualization Settings
    GRAPH_DPI = int(os.getenv("GRAPH_DPI", "300"))
    GRAPH_WIDTH = int(os.getenv("GRAPH_WIDTH", "12"))
    GRAPH_HEIGHT = int(os.getenv("GRAPH_HEIGHT", "6"))

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", str(PROJECT_ROOT / "logs" / "translation_agents.log"))

    # Performance Settings
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))
    PARALLEL_PROCESSING = os.getenv("PARALLEL_PROCESSING", "false").lower() == "true"

    # Development Settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        for directory in [cls.CACHE_DIR, cls.RESULTS_DIR, cls.SCREENSHOTS_DIR, Path(cls.LOG_FILE).parent]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_embedding_cache_path(cls, text_hash: str) -> Path:
        """Get the cache file path for a given text hash."""
        return Path(cls.CACHE_DIR) / f"embedding_{text_hash}.npy"

    @classmethod
    def to_dict(cls) -> dict:
        """Return configuration as dictionary (useful for logging)."""
        return {
            "embedding_model": cls.EMBEDDING_MODEL,
            "cache_dir": cls.CACHE_DIR,
            "enable_cache": cls.ENABLE_CACHE,
            "input_file": cls.INPUT_FILE,
            "output_file": cls.OUTPUT_FILE,
            "graph_output": cls.GRAPH_OUTPUT,
            "debug_mode": cls.DEBUG_MODE,
            "verbose": cls.VERBOSE,
        }


# Ensure directories exist on module load
Config.ensure_directories()
