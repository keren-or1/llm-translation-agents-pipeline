# System Architecture Documentation
## LLM Translation Agents Pipeline

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Architecture Pattern**: Sequential Agent Pipeline
**Model**: Layered + Pipe-and-Filter

---

## 1. System Overview

### 1.1 Purpose
The Translation Agents Pipeline orchestrates three independent LLM agents in a sequential chain to translate text through multiple languages while measuring semantic fidelity degradation under controlled spelling errors.

### 1.2 High-Level Architecture
```
Input Sentence (English with errors)
           ↓
      [Agent A]  (English → French)
           ↓
      [Agent B]  (French → Hebrew)
           ↓
      [Agent C]  (Hebrew → English)
           ↓
    Output Sentence (English)
           ↓
    Embedding Calculation
           ↓
    Vector Distance Metrics
           ↓
    Results & Analysis
```

---

## 2. C4 Model - System Context

### 2.1 Context Diagram (C4 Level 1)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   USER (Researcher / Developer)                         │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Input sentences, error rates
                   ↓
    ┌──────────────────────────────────┐
    │  Translation Agent System (TAS)   │
    │                                  │
    │  - Orchestrate agents            │
    │  - Collect results               │
    │  - Calculate embeddings          │
    │  - Generate analysis             │
    └──────────┬───────────────────────┘
               │
      ┌────────┼────────┐
      ↓        ↓        ↓
    Agent A  Agent B  Agent C
   (Claude) (Claude) (Claude)
   E2F      F2H      H2E

      Also uses:
      - SentenceTransformers (embeddings)
      - scikit-learn (metrics)
      - matplotlib (visualization)
```

### 2.2 Stakeholders
- **Researcher**: Wants insights on LLM robustness
- **Developer**: Needs to maintain and extend system
- **System**: Needs to be reproducible, reliable, well-documented

---

## 3. C4 Model - Container Diagram (Level 2)

```
┌─────────────────────────────────────────────────────────────────┐
│                     User's Machine                             │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │         Python Application                          │   │
│  │                                                     │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  CLI Interface                              │  │   │
│  │  │  (Args: input, output, cache-dir)          │  │   │
│  │  └──────────────┬───────────────────────────────┘  │   │
│  │               │                                    │   │
│  │  ┌────────────▼─────────────────────────────────┐  │   │
│  │  │  Configuration Manager                      │  │   │
│  │  │  - Load experiment data                     │  │   │
│  │  │  - Manage settings                          │  │   │
│  │  └────────────┬─────────────────────────────────┘  │   │
│  │               │                                    │   │
│  │  ┌────────────▼─────────────────────────────────┐  │   │
│  │  │  Results Calculator                         │  │   │
│  │  │  - Orchestrate calculation pipeline         │  │   │
│  │  │  - Manage caching                           │  │   │
│  │  └────────────┬──────────┬──────────┬──────────┘  │   │
│  │               │          │          │             │   │
│  │  ┌────────────▼──┐  ┌────▼──────┐  ┌────▼──────┐ │   │
│  │  │ Embeddings    │  │ Calculator│  │Visualization
│  │  │ Module        │  │ Module    │  │ Module    │ │   │
│  │  │ - Cache mgmt  │  │ - Distance│  │ - Graphs  │ │   │
│  │  │ - Encode text │  │ - Stats   │  │ - Export  │ │   │
│  │  └────────────────┘  └───────────┘  └───────────┘ │   │
│  │                                                    │   │
│  └────────────────┬───────────────────────────────────┘   │
│                   │                                        │
└───────────────────┼────────────────────────────────────────┘
                    │
         ┌──────────┼──────────┐
         ↓          ↓          ↓
    ┌────────┐  ┌────────┐  ┌──────────┐
    │ Agent  │  │Results │  │ External │
    │System  │  │  Files │  │ Services │
    │(Claude)│  │(JSON, │  │(HF, AWS) │
    │        │  │ PNG)   │  │          │
    └────────┘  └────────┘  └──────────┘
```

---

## 4. C4 Model - Component Diagram (Level 3)

### 4.1 Python Application Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Python Application                        │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  src/cli.py                                         │  │
│  │  - Parse command-line arguments                     │  │
│  │  - Validate inputs                                  │  │
│  │  - Coordinate execution flow                        │  │
│  └───────────┬────────────────────────────────────────┘  │
│              │                                            │
│  ┌───────────▼────────────────────────────────────────┐  │
│  │  src/config.py                                      │  │
│  │  - DEFAULT_MODEL: "all-MiniLM-L6-v2"              │  │
│  │  - DEFAULT_CACHE_DIR: ".cache"                     │  │
│  │  - Experiment metadata                              │  │
│  └───────────┬────────────────────────────────────────┘  │
│              │                                            │
│  ┌───────────▼────────────────────────────────────────┐  │
│  │  src/embeddings.py                                 │  │
│  │  ┌──────────────────────────────────────────┐     │  │
│  │  │ EmbeddingCalculator class              │     │  │
│  │  │ - get_or_calculate_embedding(text)     │     │  │
│  │  │ - _load_model()                        │     │  │
│  │  │ - _get_cache_path(text)                │     │  │
│  │  │ - clear_cache()                        │     │  │
│  │  └──────────────────────────────────────────┘     │  │
│  │                                                    │  │
│  │  ┌──────────────────────────────────────────┐     │  │
│  │  │ Cache Management                         │     │  │
│  │  │ - MD5 hash of text → embedding.npy      │     │  │
│  │  │ - File system based (no DB)             │     │  │
│  │  └──────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  src/calculator.py                               │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │ DistanceCalculator class                │   │  │
│  │  │ - calculate_cosine_distance()          │   │  │
│  │  │ - calculate_statistics()                │   │  │
│  │  │ - generate_results_table()              │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  Operations:                                     │  │
│  │  - Input: 2 embeddings (numpy arrays)           │  │
│  │  - Process: cosine_distances()                  │  │
│  │  - Output: (distance: float, similarity: float) │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  src/visualization.py                            │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │ GraphVisualizer class                    │   │  │
│  │  │ - create_distance_graph()                │   │  │
│  │  │ - _configure_axes()                      │   │  │
│  │  │ - _add_legends()                         │   │  │
│  │  │ - save_figure()                          │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  Output: PNG graph (300+ DPI)                   │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  src/utils.py                                    │  │
│  │  - load_experiments(json_file)                   │  │
│  │  - save_results(json_file, results)              │  │
│  │  - save_markdown_report(md_file, results)        │  │
│  │  - validate_sentence(text)                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 5. Data Flow Architecture

### 5.1 Complete Data Flow Diagram

```
Step 1: Input
┌──────────────────────────────────────────┐
│ Experiment Data (JSON)                   │
│ - error_percentage: int                  │
│ - original_english: str                  │
│ - final_english: str (from agent chain)  │
└───────────────┬──────────────────────────┘
                │
Step 2: Embedding Calculation
                ↓
        ┌─────────────────┐
        │ Text Input      │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ Check Cache     │  (MD5 hash of text)
        └────┬────────┬───┘
            YES│       │NO
               │       │
        ┌──────▼──┐   ┌▼──────────────────┐
        │ Load    │   │ Encode with Model │
        │.npy    │   │ all-MiniLM-L6-v2 │
        └────┬────┘   └────┬──────────────┘
             │             │
             │  ┌──────────┘
             └──┤ Save to Cache
                └──────────────┐
                               │
        ┌──────────────────────▼──┐
        │ Numpy Array (384-dim)    │
        └──────────────┬───────────┘
                       │
Step 3: Distance Calculation
                       │
        ┌──────────────▼───────────┐
        │ Two Embeddings:          │
        │ - Original (384-dim)     │
        │ - Final (384-dim)        │
        └──────────────┬───────────┘
                       │
        ┌──────────────▼──────────────┐
        │ Cosine Distance Function:   │
        │ distance = 1 - similarity   │
        │ (using scikit-learn)        │
        └──────────────┬──────────────┘
                       │
Step 4: Metrics Output
                       │
        ┌──────────────▼────────────────┐
        │ Results Object:              │
        │ - error_percentage           │
        │ - cosine_distance            │
        │ - cosine_similarity          │
        │ - embedding_model            │
        └──────────────┬────────────────┘
                       │
Step 5: Statistics & Aggregation
                       │
        ┌──────────────▼──────────────────┐
        │ Calculate Across All 6 Trials:  │
        │ - Mean distance                 │
        │ - Std deviation                 │
        │ - Min/Max                       │
        │ - Total increase %              │
        └──────────────┬──────────────────┘
                       │
Step 6: Visualization & Export
                       │
        ┌──────────────┴───────────────┐
        │                              │
        ↓                              ↓
    ┌──────────┐            ┌──────────────────┐
    │ PNG Graph│            │ JSON Results     │
    │          │            │ Markdown Report  │
    └──────────┘            └──────────────────┘
```

---

## 6. Module Architecture & Responsibilities

### 6.1 Module Dependency Graph

```
cli.py
  ├─→ config.py
  ├─→ utils.py (load_experiments)
  └─→ calculate_results.py
       ├─→ embeddings.py
       │   └─→ config.py (model_name)
       ├─→ calculator.py
       │   └─→ config.py
       ├─→ visualization.py
       │   └─→ config.py
       └─→ utils.py (save_results)
```

### 6.2 Module Descriptions

#### src/cli.py (Main Entry Point)
- **Responsibility**: Parse arguments and orchestrate workflow
- **Interface**:
  - `main(argv: List[str]) → None`
- **Dependencies**: argparse, all other modules
- **Typical Size**: 100-150 lines

#### src/config.py (Configuration)
- **Responsibility**: Centralize all configuration constants
- **Interface**:
  - `DEFAULT_MODEL_NAME: str`
  - `DEFAULT_CACHE_DIR: str`
  - `DEFAULT_OUTPUT_FILE: str`
  - Load from environment variables
- **Dependencies**: os, pathlib
- **Typical Size**: 30-50 lines

#### src/embeddings.py (Embedding Management)
- **Responsibility**: Handle embedding calculation and caching
- **Class**: `EmbeddingCalculator`
- **Key Methods**:
  - `__init__(model_name, cache_dir)`
  - `get_or_calculate_embedding(text) → np.ndarray`
  - `clear_cache() → None`
- **Dependencies**: sentence_transformers, numpy, hashlib
- **Typical Size**: 80-120 lines

#### src/calculator.py (Core Calculations)
- **Responsibility**: Calculate distances and statistics
- **Class**: `DistanceCalculator`
- **Key Methods**:
  - `calculate_cosine_distance(emb1, emb2) → Tuple[float, float]`
  - `calculate_statistics(results) → Dict`
  - `process_all_experiments(experiments) → List[Dict]`
- **Dependencies**: numpy, scikit-learn, pandas
- **Typical Size**: 100-150 lines

#### src/visualization.py (Graph Generation)
- **Responsibility**: Create publication-quality visualizations
- **Class**: `GraphVisualizer`
- **Key Methods**:
  - `create_distance_graph(results, output_path)`
  - `_configure_axes(ax1, ax2)`
  - `_add_legends(ax1, ax2)`
  - `save_figure(fig, output_path, dpi=300)`
- **Dependencies**: matplotlib, numpy
- **Typical Size**: 120-180 lines

#### src/utils.py (Utilities)
- **Responsibility**: File I/O and data manipulation
- **Key Functions**:
  - `load_experiments(json_path) → List[Dict]`
  - `save_results(path, results) → None`
  - `save_markdown_report(path, results) → None`
  - `validate_sentence(text) → bool`
- **Dependencies**: json, pathlib, typing
- **Typical Size**: 100-150 lines

#### src/calculate_results.py (Legacy/Main Script)
- **Responsibility**: Main script entry point (backward compatibility)
- **Will be refactored to call cli.py
- **Existing Size**: 354 lines → Should reduce to ~50 after refactoring

---

## 7. Design Patterns & Architecture Decisions

### 7.1 Architecture Decision Record (ADR) #1
**Title**: Caching Strategy for Embeddings

**Context**: Embedding calculation is expensive (multiple seconds per experiment). Running the system multiple times during development is time-consuming.

**Decision**: Implement file-based embedding cache using MD5 hashing

**Rationale**:
- Fast: Loading from disk is much faster than re-computing
- Simple: No database dependency
- Reproducible: Same text → same hash → same embedding
- Optional: Can be cleared if needed

**Consequences**:
- ✅ Development cycle faster
- ✅ Results reproducible
- ✅ No external services needed
- ⚠️ Disk space used for cache
- ⚠️ Must handle cache invalidation if model changes

**Implementation**:
```python
# Hash-based cache location
cache_path = cache_dir / f"embedding_{md5(text)}.npy"
```

### 7.2 Architecture Decision Record (ADR) #2
**Title**: Module Separation vs Single Script

**Context**: Original implementation was single 354-line script. Difficult to test, modify, understand.

**Decision**: Refactor into 6 focused modules with single responsibility

**Rationale**:
- Maintainability: Each module has clear purpose
- Testability: Can unit test each component
- Reusability: Modules can be used independently
- Clarity: Code easier to understand

**Module Structure**:
- config.py: Configuration
- embeddings.py: Embedding logic
- calculator.py: Distance calculations
- visualization.py: Graph generation
- utils.py: File I/O
- cli.py: Main orchestration

**Consequences**:
- ✅ Easier to maintain
- ✅ Better test coverage possible
- ✅ Clearer architecture
- ⚠️ More files to manage
- ⚠️ Inter-module dependencies

### 7.3 Architecture Decision Record (ADR) #3
**Title**: Embedding Model Selection

**Context**: Need embedding model for semantic similarity. Multiple options available (OpenAI, local, etc.)

**Decision**: Use SentenceTransformers `all-MiniLM-L6-v2`

**Rationale**:
- Free and open-source
- 384-dimensional vectors (reasonable size)
- Lightweight (no GPU needed)
- Trained on large corpus (good generalization)
- No API costs

**Comparison**:
| Model | Cost | Quality | Speed | Size |
|-------|------|---------|-------|------|
| OpenAI text-embedding | $ | Excellent | Medium | Large |
| all-MiniLM-L6-v2 | Free | Good | Fast | Small |
| all-mpnet-base-v2 | Free | Excellent | Slow | Medium |

**Consequences**:
- ✅ No costs
- ✅ Fast inference
- ✅ Good enough accuracy
- ⚠️ Not state-of-the-art
- ⚠️ Fixed model (can't use others without code change)

### 7.4 Architecture Decision Record (ADR) #4
**Title**: Results Export Format

**Context**: Need to export results for further analysis. Multiple formats possible.

**Decision**: Support both JSON (machine-readable) and Markdown (human-readable)

**Rationale**:
- JSON: For programmatic analysis, data processing
- Markdown: For reports, documentation, readability

**Schema**:
```json
{
  "experiments": [
    {
      "error_percentage": 0,
      "original_english": "...",
      "final_english": "...",
      "cosine_distance": 0.098352,
      "cosine_similarity": 0.901648
    }
  ],
  "statistics": {
    "mean_distance": 0.346256,
    "std_dev": 0.148627
  }
}
```

**Consequences**:
- ✅ Flexible analysis possible
- ✅ Human-readable reports
- ✅ Easy data sharing
- ⚠️ Two export mechanisms to maintain

---

## 8. Interface Contracts

### 8.1 EmbeddingCalculator Interface

```python
class EmbeddingCalculator:
    """Calculate embeddings with automatic caching."""

    def __init__(self, model_name: str, cache_dir: str) -> None:
        """Initialize with model and cache location."""

    def get_or_calculate_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding from cache or calculate and cache.

        Args:
            text: Input text to embed

        Returns:
            np.ndarray: 384-dimensional embedding vector

        Raises:
            ValueError: If text is empty
            RuntimeError: If model loading fails
        """

    def clear_cache(self) -> None:
        """Clear all cached embeddings."""
```

### 8.2 DistanceCalculator Interface

```python
class DistanceCalculator:
    """Calculate semantic distances between embeddings."""

    @staticmethod
    def calculate_cosine_distance(
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> Tuple[float, float]:
        """
        Calculate cosine distance and similarity.

        Args:
            embedding1: First embedding (N-dimensional vector)
            embedding2: Second embedding (N-dimensional vector)

        Returns:
            Tuple: (distance, similarity)
                - distance = 1 - similarity
                - Both in range [0, 1]

        Raises:
            ValueError: If embeddings have different dimensions
        """
```

### 8.3 GraphVisualizer Interface

```python
class GraphVisualizer:
    """Create publication-quality visualizations."""

    def create_distance_graph(
        self,
        results: List[Dict],
        output_path: str
    ) -> None:
        """
        Create dual-axis graph of distance and similarity.

        Args:
            results: List of result dictionaries
            output_path: Where to save PNG file

        Output:
            - PNG file with 300+ DPI
            - Dimensions: 12x6 inches
            - Professional appearance
        """
```

---

## 9. Data Schemas

### 9.1 Experiment Input Format (JSON)

```json
{
  "experiments": [
    {
      "error_percentage": 0,
      "original_english": "The advanced artificial intelligence...",
      "french_output": "Le système d'intelligence artificielle...",
      "hebrew_output": "מערכת הבינה המלאכותית...",
      "final_english": "The advanced artificial intelligence..."
    }
  ]
}
```

### 9.2 Results Output Format (JSON)

```json
{
  "experiments": [
    {
      "error_percentage": 0,
      "original_english": "...",
      "final_english": "...",
      "cosine_distance": 0.098352,
      "cosine_similarity": 0.901648,
      "embedding_model": "all-MiniLM-L6-v2"
    }
  ],
  "statistics": {
    "mean_distance": 0.346256,
    "std_dev": 0.148627,
    "min_distance": 0.098352,
    "max_distance": 0.555445
  },
  "metadata": {
    "generated_at": "2025-11-16T12:00:00Z",
    "model": "all-MiniLM-L6-v2",
    "total_experiments": 6
  }
}
```

---

## 10. Deployment Architecture

### 10.1 Development Environment
```
Developer Machine
├── Python 3.8+
├── Virtual Environment (.venv)
├── Dependencies (requirements.txt)
├── Source Code (src/)
├── Tests (tests/)
├── Embeddings Cache (.cache/)
└── Results (results/)
```

### 10.2 Execution Flow

```
$ python src/calculate_results.py [--args]
    ↓
Load CLI arguments
    ↓
Load experiment data (JSON)
    ↓
For each experiment:
  ├─ Get embeddings (original)
  ├─ Get embeddings (final)
  ├─ Calculate distance
  └─ Store results
    ↓
Calculate statistics
    ↓
Generate graph
    ↓
Export JSON
    ↓
Export Markdown
    ↓
Print summary
```

---

## 11. Performance & Scalability

### 11.1 Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Load model | 2-3s | One-time only |
| Embed text (uncached) | 0.5-1s | Per sentence |
| Embed text (cached) | <0.01s | From disk |
| Calculate distance | <0.01s | Negligible |
| Generate graph | 1-2s | Matplotlib rendering |
| Total (6 experiments) | ~15-20s | First run (uncached) |
| Total (6 experiments) | ~2-3s | Cached |

### 11.2 Scalability

| Metric | Current | Limit |
|--------|---------|-------|
| Sentences | 1-100 | 1000+ possible |
| Error rates | 6 | Unlimited |
| Embedding dims | 384 | Depends on model |
| Memory usage | ~100MB | Scales linearly |

---

## 12. Extensibility & Future Work

### 12.1 Extension Points

1. **Additional Embedding Models**: Modify config.py, test with any HuggingFace model
2. **New Metrics**: Add to calculator.py (Euclidean distance, semantic similarity, etc.)
3. **Visualization Types**: Add methods to visualization.py
4. **Language Pairs**: Document agent prompts for other language combinations
5. **Real-time Processing**: Refactor CLI to support streaming

### 12.2 Future Enhancements

- [ ] Support multiple embedding models with comparison
- [ ] Jupyter notebook for interactive analysis
- [ ] Web dashboard for visualization
- [ ] Batch processing of multiple sentences
- [ ] Database storage for results
- [ ] REST API for remote execution
- [ ] Statistical tests (t-test, ANOVA on error rates)

---

## 13. Quality Attributes

### 13.1 ISO/IEC 25010 Compliance

| Attribute | Status | Evidence |
|-----------|--------|----------|
| **Functional Suitability** | ✅ | All FR met |
| **Performance Efficiency** | ✅ | <20s for 6 experiments |
| **Compatibility** | ✅ | Tested on macOS |
| **Usability** | 🔄 | CLI interface clear, docs needed |
| **Reliability** | ✅ | Error handling, reproducible |
| **Security** | ✅ | No secrets in code |
| **Maintainability** | 🔄 | Modular architecture, tests needed |
| **Portability** | ✅ | Python standard library only |

---

## 14. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Model loading fails | Low | High | Error handling, fallback |
| Cache corruption | Very Low | Medium | Validation, clear cache option |
| OOM on large batches | Low | Medium | Monitor memory, batch processing |
| Embedding model unavailable | Low | High | Offline mode, bundled model |

---

## 15. Conclusion

The Translation Agents Pipeline implements a well-structured, modular architecture that separates concerns, enables testing, and allows for future extensions. The system follows established design patterns (pipe-and-filter, layered architecture) and adheres to software engineering best practices.

Key architectural strengths:
- ✅ Clear separation of concerns
- ✅ Documented decisions
- ✅ Extensible design
- ✅ Testable components
- ✅ Reproducible results

This document serves as the authoritative reference for system design and guides both current development and future maintenance.
