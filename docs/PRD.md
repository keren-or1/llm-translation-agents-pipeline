# Product Requirements Document (PRD)
## Translation Agent System with Vector Distance Analysis

**Version**: 1.0
**Date**: November 2025
**Author**: Assignment 3 Submission
**Status**: Implementation Complete

---

## 1. Executive Summary

This project implements a three-agent LLM translation pipeline that simulates a "Turing Machine" through sequential translation: English → French → Hebrew → English. The system tests robustness to spelling errors and measures semantic distance using vector embeddings.

### Problem Statement
How do spelling errors in input text affect the semantic fidelity of output after passing through a multi-stage LLM translation pipeline?

### Solution
A Python-based system that:
- Processes text through three sequential translation agents
- Calculates vector embeddings for original and final English text
- Measures cosine distance to quantify semantic drift
- Generates visualizations and statistical analysis

---

## 2. Goals and Success Metrics

### Primary Goals
1. Implement functional three-agent translation pipeline
2. Measure semantic distance across error percentages (0%, 10%, 20%, 30%, 40%, 50%)
3. Generate publication-quality visualizations
4. Provide comprehensive documentation

### Key Performance Indicators (KPIs)
- **Accuracy**: System correctly processes all experiments
- **Performance**: Embedding calculation completes in <30 seconds total
- **Reliability**: Results reproducible through caching mechanism
- **Usability**: Clear documentation enables independent execution

### Acceptance Criteria
- All 6 error-rate experiments successfully processed
- Cosine distance calculated with 6 decimal precision
- Graph generated showing distance vs. error percentage
- Complete documentation of agent prompts and methodology

---

## 3. Functional Requirements

### FR-1: Experiment Data Management
**Priority**: High
**Description**: System must load and process experiment data
**Requirements**:
- Load experiments from JSON input file
- Support backward compatibility with hardcoded defaults
- Validate data structure (error_percentage, original_english, final_english)

### FR-2: Embedding Calculation
**Priority**: High
**Description**: Calculate semantic embeddings using SentenceTransformer
**Requirements**:
- Use all-MiniLM-L6-v2 model (384 dimensions)
- Cache embeddings using MD5 hash for text identification
- Support cache clearing via CLI flag

### FR-3: Distance Measurement
**Priority**: High
**Description**: Calculate cosine distance between embeddings
**Requirements**:
- Compute cosine distance (1 - cosine similarity)
- Return both distance and similarity metrics
- Provide 6 decimal precision

### FR-4: Visualization Generation
**Priority**: High
**Description**: Create publication-quality graphs
**Requirements**:
- Dual-panel figure (distance + similarity)
- 300 DPI resolution for publication
- Clear labels, legends, and annotations
- Save as PNG format

### FR-5: CLI Interface
**Priority**: Medium
**Description**: Command-line interface for flexible execution
**Requirements**:
- Support arguments: --input, --output, --graph-output, --cache-dir, --clear-cache
- Provide helpful error messages
- Display progress indicators

### FR-6: Results Export
**Priority**: High
**Description**: Save results in machine-readable format
**Requirements**:
- Export JSON with all experimental data
- Include both distance and similarity
- UTF-8 encoding support

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Embedding calculation: <5 seconds per sentence (cached: <0.1 seconds)
- Total execution time: <2 minutes for 6 experiments
- Memory usage: <2GB

### NFR-2: Scalability
- Support experiments with 10-100 sentences
- Cache directory can grow to 100MB
- Modular design allows adding new experiments

### NFR-3: Maintainability
- Code files limited to 150 lines maximum
- Comprehensive docstrings for all functions/classes
- Clear separation of concerns (embedding, visualization, data processing)

### NFR-4: Usability
- One-command execution for default experiments
- Clear documentation in README
- Example usage patterns provided

### NFR-5: Security
- No hardcoded API keys
- Support for environment variables (.env)
- .gitignore prevents accidental secret commits

---

## 5. Technical Requirements

### 5.1 Dependencies
- Python 3.8+
- sentence-transformers >= 2.2.0
- scikit-learn >= 1.0.0
- numpy >= 1.21.0
- pandas >= 1.3.0
- matplotlib >= 3.4.0

### 5.2 Input Format
```json
{
  "experiments": [
    {
      "error_percentage": 0,
      "original_english": "...",
      "final_english": "..."
    }
  ]
}
```

### 5.3 Output Format
```json
[
  {
    "error_percentage": 0,
    "original_english": "...",
    "final_english": "...",
    "cosine_distance": 0.098352,
    "cosine_similarity": 0.901648
  }
]
```

---

## 6. User Stories

### US-1: Researcher Running Experiments
**As a** researcher
**I want to** process translation experiments with different error rates
**So that** I can quantify semantic drift in LLM translation pipelines

**Acceptance Criteria**:
- Execute with single command
- View real-time progress
- Get statistical summary at completion

### US-2: Developer Extending System
**As a** developer
**I want** well-documented, modular code
**So that** I can add new embedding models or metrics

**Acceptance Criteria**:
- Each module <150 lines
- Comprehensive docstrings
- Clear separation of concerns

### US-3: Academic Using Results
**As an** academic researcher
**I want** publication-quality visualizations
**So that** I can include results in papers

**Acceptance Criteria**:
- 300 DPI resolution
- Professional styling
- Clear axis labels and legends

---

## 7. Constraints and Assumptions

### Constraints
- **No Python agent execution**: Agents must be invoked via CLI (e.g., Claude Code)
- **Python only for embeddings**: Translation cannot use Python automation
- **File size limit**: Code files must not exceed 150 lines
- **Assignment requirements**: Must follow academic submission guidelines

### Assumptions
- Users have Python 3.8+ installed
- Users have sufficient disk space for embedding cache
- Input text is in English (for original_english field)
- SentenceTransformer models are accessible online

---

## 8. Dependencies and External Systems

### External Dependencies
- **Hugging Face**: SentenceTransformer model hosting
- **Claude Code CLI**: For agent invocation (manual process)

### Internal Dependencies
- embedding_calculator.py → data_processor.py
- calculate_results.py → all modules

---

## 9. Timeline and Milestones

| Milestone | Description | Status |
|-----------|-------------|--------|
| M1 | Agent definition and system prompt creation | ✓ Complete |
| M2 | Manual execution of 6 experiments | ✓ Complete |
| M3 | Python embedding calculator implementation | ✓ Complete |
| M4 | Visualization and analysis | ✓ Complete |
| M5 | Documentation and README | ✓ Complete |

---

## 10. Risks and Mitigation

### Risk 1: Embedding Model Unavailable
**Impact**: High
**Probability**: Low
**Mitigation**: Cache all embeddings; provide fallback model options

### Risk 2: Memory Constraints
**Impact**: Medium
**Probability**: Low
**Mitigation**: Process experiments sequentially; use efficient numpy operations

### Risk 3: API Rate Limiting (if using external APIs)
**Impact**: Medium
**Probability**: Medium
**Mitigation**: Implement caching; provide retry logic

---

## 11. Open Questions

None - all requirements defined and implemented.

---

## 12. Appendix

### Related Documents
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [METHODOLOGY.md](./METHODOLOGY.md) - Experimental methodology
- [README.md](../README.md) - User documentation

### References
- Assignment instructions (assignment.txt)
- Software submission guidelines (software_submission_guidelines.pdf)
- SentenceTransformers documentation
