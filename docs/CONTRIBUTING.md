# Contributing to Translation Agents Pipeline

Thank you for your interest in contributing to the Translation Agents Pipeline! This document provides guidelines and instructions for contributing code, documentation, and improvements to the project.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style & Standards](#code-style--standards)
4. [Making Changes](#making-changes)
5. [Adding Features](#adding-features)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Submitting Changes](#submitting-changes)

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)
- Basic understanding of LLMs and embeddings

### Core Concepts
Before contributing, understand:
- **Agent Architecture**: Three-stage translation pipeline
- **Embedding-based Evaluation**: Cosine distance metrics
- **Modular Design**: Separation of concerns across modules

---

## Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd llm-translation-agents-pipeline
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-cov  # For testing
```

### 4. Set Up Environment Variables
```bash
cp .env.example .env
# Modify .env if you need custom settings
```

### 5. Verify Installation
```bash
python -c "from src.calculate_results import ExperimentResultsCalculator; print('✓ Installation successful')"
```

---

## Code Style & Standards

### Python Code Style

We follow **PEP 8** with the following conventions:

#### Naming Conventions
```python
# Classes: PascalCase
class EmbeddingCalculator:
    pass

# Functions/methods: snake_case
def calculate_cosine_distance(vec1, vec2):
    pass

# Constants: UPPER_CASE
DEFAULT_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

#### Code Organization
```python
"""
Module docstring describing the module's purpose.
List main classes/functions available.
"""

import standard_library
import third_party
from . import local_imports

# Constants
DEFAULT_VALUE = 42

# Global variables (rare)
_global_state = {}

# Classes
class MyClass:
    """Class docstring."""

    def __init__(self):
        pass

    def public_method(self):
        """Public method docstring."""
        pass

# Functions
def my_function():
    """Function docstring."""
    pass
```

#### Docstring Format
```python
def calculate_cosine_distance(embedding1, embedding2):
    """
    Calculate cosine distance and similarity between embeddings.

    Args:
        embedding1 (np.ndarray): First embedding vector (N-dimensional)
        embedding2 (np.ndarray): Second embedding vector (N-dimensional)

    Returns:
        Tuple[float, float]: (distance, similarity) where:
            - distance = 1 - similarity
            - Both in range [0, 1]

    Raises:
        ValueError: If embeddings have different dimensions
        TypeError: If inputs are not numpy arrays

    Example:
        >>> emb1 = np.array([1.0, 0.0])
        >>> emb2 = np.array([0.0, 1.0])
        >>> dist, sim = calculate_cosine_distance(emb1, emb2)
        >>> assert dist == pytest.approx(1.0)
    """
```

#### Type Hints
```python
from typing import List, Dict, Tuple, Optional

def process_experiments(
    experiments: List[Dict[str, any]],
    cache_dir: str,
    verbose: bool = False
) -> List[Dict[str, float]]:
    """Process experiments and return results."""
    pass
```

### File Size Limits

- **Maximum file size**: 200 lines of code
- **Ideal file size**: 100-150 lines
- **Rationale**: Easier to test, understand, and maintain

If a file exceeds 200 lines:
1. Identify logical components
2. Extract into separate modules
3. Use imports to combine functionality

### Import Organization

```python
# Standard library (alphabetical)
import json
import logging
from pathlib import Path
from typing import Dict, List

# Third-party (alphabetical)
import numpy as np
from sklearn.metrics.pairwise import cosine_distances
from sentence_transformers import SentenceTransformer

# Local imports
from src.config import Config
from src.utils import load_experiments
```

---

## Making Changes

### Code Review Checklist

Before submitting code, verify:

**Code Quality**
- [ ] Follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Type hints present for function signatures
- [ ] No code duplication (DRY principle)
- [ ] Comments explain "why" not "what"
- [ ] < 150 lines per file

**Functionality**
- [ ] Code solves the stated problem
- [ ] No breaking changes to existing APIs
- [ ] Handles edge cases appropriately
- [ ] Error messages are clear and helpful
- [ ] Performance acceptable

**Testing**
- [ ] New code has unit tests
- [ ] All tests pass: `pytest tests/`
- [ ] Coverage maintained: `pytest --cov`
- [ ] No random failures

**Documentation**
- [ ] Docstrings updated
- [ ] README updated if needed
- [ ] Architecture documentation updated if applicable
- [ ] Examples provided if new feature

---

## Adding Features

### Feature Request Process

1. **Open an Issue**
   - Describe the feature clearly
   - Explain the use case
   - Provide examples if possible

2. **Design Phase**
   - Discuss approach in issue
   - Consider impact on existing code
   - Plan testing strategy

3. **Implementation**
   - Follow code standards above
   - Write tests first (TDD recommended)
   - Update documentation

4. **Review**
   - Request code review
   - Address feedback
   - Ensure tests pass

### Adding a New Embedding Model

Example: Adding support for OpenAI embeddings

**Step 1**: Extend config.py
```python
class Config:
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_MODELS = {
        "all-MiniLM-L6-v2": {"dimension": 384},
        "text-embedding-3-small": {"dimension": 512}
    }
```

**Step 2**: Modify embeddings.py
```python
class EmbeddingCalculator:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        if model_name == "text-embedding-3-small":
            # Use OpenAI client
            pass
        else:
            # Use SentenceTransformer
            pass
```

**Step 3**: Add tests
```python
def test_openai_embedding_dimension():
    calc = EmbeddingCalculator("text-embedding-3-small")
    emb = calc.get_or_calculate_embedding("test")
    assert emb.shape[0] == 512
```

**Step 4**: Update docs
- Update config documentation
- Add model comparison table
- Update CONTRIBUTING.md

### Adding a New Agent

Example: Adding an Agent for German

**Step 1**: Create agent documentation
- File: `docs/agent_d_hebrew_to_german.md`
- Follow existing agent documentation format
- Include system prompt and skills

**Step 2**: Test with CLI
```bash
/agents agent_d_hebrew_to_german --input "עברית"
```

**Step 3**: Document in METHODOLOGY.md
- Explain agent invocation
- Show sample results

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_calculator.py

# Run specific test
pytest tests/test_calculator.py::TestDistanceCalculation::test_identical_vectors_zero_distance

# Run with verbose output
pytest tests/ -v
```

### Writing Tests

**Test File Naming**: `test_<module>.py`
**Test Class Naming**: `Test<Component>`
**Test Function Naming**: `test_<scenario>`

**Example Test**:
```python
import pytest
import numpy as np
from src.calculator import DistanceCalculator

class TestDistanceCalculation:
    """Test distance calculation functions."""

    def test_identical_vectors_zero_distance(self):
        """Test that identical vectors produce zero distance."""
        # Arrange
        vector = np.array([1.0, 0.0, 0.0])
        expected_distance = 0.0

        # Act
        distance, similarity = DistanceCalculator.calculate_cosine_distance(vector, vector)

        # Assert
        assert distance == pytest.approx(expected_distance, abs=1e-6)
```

### Test Coverage Goals

- **Minimum**: 70% code coverage
- **Target**: 85%+ code coverage
- **Tool**: `pytest-cov`

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Documentation

### README.md Updates
- Update if API changes
- Add examples for new features
- Update installation instructions if dependencies change

### Code Documentation
- Update docstrings if function behavior changes
- Document new parameters
- Add examples in docstrings

### Architecture Documentation
- Update ARCHITECTURE.md if system design changes
- Document new modules
- Update dependency diagrams

### ANALYSIS.md Updates
- Add new findings if applicable
- Update formulas if metrics change
- Document new sensitivity analysis

---

## Submitting Changes

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes**
   - Commit frequently with clear messages
   - Follow commit message conventions

3. **Commit Message Format**
   ```
   feat: Add support for OpenAI embeddings

   - Extend EmbeddingCalculator to support OpenAI API
   - Add configuration options for model selection
   - Update tests with OpenAI embedding tests

   Fixes #123
   ```

4. **Push to Feature Branch**
   ```bash
   git push origin feature/my-feature
   ```

5. **Create Pull Request**
   - Clear title: "feat: Add OpenAI embedding support"
   - Description: Explain changes and rationale
   - Link related issues
   - Request review

### Pull Request Checklist

- [ ] Feature branch created from `main`
- [ ] Commits have clear, descriptive messages
- [ ] Code passes linting: `pylint src/`
- [ ] Tests pass: `pytest tests/ --cov=src`
- [ ] Documentation updated
- [ ] No breaking changes to public APIs
- [ ] CHANGELOG.md updated (if applicable)

### Code Review Process

1. **Reviewer Checks**
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - No obvious bugs

2. **Author Responds**
   - Address feedback
   - Request re-review if changes made

3. **Approval & Merge**
   - Reviewer approves
   - Author merges to main
   - Delete feature branch

---

## Best Practices

### Code Reusability
- Extract common logic into `utils.py`
- Create functions for repeated patterns
- Document reusable functions well

### Error Handling
```python
def load_experiments(file_path):
    """Load experiments from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data.get('experiments', [])
    except FileNotFoundError:
        raise FileNotFoundError(f"Experiment file not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in file: {file_path}")
```

### Performance Considerations
- Cache expensive calculations
- Avoid unnecessary file I/O
- Batch process when possible
- Document performance trade-offs

### Version Compatibility
- Test on Python 3.8, 3.9, 3.10, 3.11
- Use type hints for clarity
- Document minimum requirements

---

## Questions or Need Help?

- Check existing issues: `https://github.com/...`
- Review documentation in `docs/`
- Look at existing code examples
- Ask in project discussions

---

## Code of Conduct

- Be respectful and inclusive
- Assume good intent
- Welcome diverse perspectives
- Provide constructive feedback

---

Thank you for contributing! Your improvements make this project better for everyone.

**Happy coding! 🚀**
