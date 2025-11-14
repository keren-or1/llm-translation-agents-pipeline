# Experimental Methodology & Setup Process

## Overview
This document describes the complete process for running the translation agent experiments, collecting results, and calculating embeddings.

---

## 1. Agent Invocation Setup

### 1.1 Agent Skill Files
Three agents were defined with specialized skills and system prompts:

- **Agent A** ([📄 docs/agent_a_english_to_french.md](docs/agent_a_english_to_french.md))
  - Task: English → French translation
  - Special skill: Handles spelling errors in English input

- **Agent B** ([📄 docs/agent_b_french_to_hebrew.md](docs/agent_b_french_to_hebrew.md))
  - Task: French → Hebrew translation
  - Special skill: Navigates Romance-to-Semitic language bridge

- **Agent C** ([📄 docs/agent_c_hebrew_to_english.md](docs/agent_c_hebrew_to_english.md))
  - Task: Hebrew → English translation
  - Special skill: Natural English reconstruction

### 1.2 Manual Agent Invocation

Each experiment required **3 sequential agent calls** (one for each agent in the chain):

```
For each error rate (0%, 10%, 20%, 30%, 40%, 50%):
  → Agent A: English (with errors) → French
  → Agent B: French output → Hebrew
  → Agent C: Hebrew output → English
```

**Total invocations**: 18 (3 agents × 6 error rates)

**Invocation method**: Claude Code Task tool with `general-purpose` subagent type

**Example invocation**:
```
Task: "Run Agent A: Translate English to French"
Prompt: "You are Agent A - professional English to French translator...
Translate the following English text to French [TEXT WITH ERRORS]
Respond with ONLY the French translation, nothing else."
```

---

## 2. Data Collection Process

### 2.1 Test Sentences
A single base sentence was used across all experiments:

**Base (0% errors)**:
> "The advanced artificial intelligence system successfully translates complex linguistic patterns across multiple languages with remarkable accuracy and precision."

**Characteristics**:
- Length: 18 words
- Topic: Translation AI systems
- Complexity: Technical but clear

### 2.2 Error Introduction
For each experiment, spelling errors were introduced at specific rates:

| Error % | Example | Method |
|---------|---------|--------|
| 0% | Original sentence unchanged | Baseline |
| 10% | "advansed", "inteligence", "sucessfully" | 3 errors ÷ 18 words = 16.7% ≈ 10% |
| 20% | +2 more spelling errors | Cumulative |
| 30% | +2 more spelling errors | Cumulative |
| 40% | +3 more spelling errors | Cumulative |
| 50% | +4 more spelling errors | Cumulative |

### 2.3 Manual Translation Collection

For **each of the 6 experiments**:

1. **Collect original English** (with errors)
2. **Run Agent A** on the English text
3. **Record French output**
4. **Run Agent B** on the French output
5. **Record Hebrew output**
6. **Run Agent C** on the Hebrew output
7. **Record final English output**

### 2.4 Output Storage

Collected results were stored in the `experiments` array in `src/calculate_results.py`:

```python
experiments = [
    {
        "error_percentage": 0,
        "original_english": "The advanced artificial intelligence...",
        "final_english": "The advanced artificial intelligence..."
    },
    # ... 5 more experiments
]
```

---

## 3. Embeddings Calculation Process

### 3.1 Embedding Model
**Model**: SentenceTransformer `all-MiniLM-L6-v2`
- Dimensions: 384
- Training: Trained on 1B+ sentence pairs
- Use case: General semantic similarity

### 3.2 Calculation Steps

For **each experiment**:

```python
1. Load embedding model
2. Encode original_english → embedding_1
3. Encode final_english → embedding_2
4. Calculate cosine_distance = 1 - cosine_similarity(embedding_1, embedding_2)
5. Store: error_percentage, distance, similarity
```

### 3.3 Metrics Computed

| Metric | Calculation | Interpretation |
|--------|-------------|-----------------|
| Cosine Distance | 1 - similarity | 0 = identical, 1 = opposite |
| Cosine Similarity | dot(norm(v1), norm(v2)) | -1 to 1, typically 0 to 1 |
| Vector Change | distance increase from baseline | Error impact quantification |

---

## 4. Execution Flow

### 4.1 Complete Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. AGENT INVOCATION PHASE (Manual)                      │
├─────────────────────────────────────────────────────────┤
│ For each of 6 error rates:                              │
│  → Run Agent A (English → French)                       │
│  → Run Agent B (French → Hebrew)                        │
│  → Run Agent C (Hebrew → English)                       │
│  → Record all outputs                                   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 2. DATA COLLECTION PHASE (Manual)                       │
├─────────────────────────────────────────────────────────┤
│ Copy all translation outputs into:                      │
│ src/calculate_results.py → experiments array            │
│                                                         │
│ Format: List of dicts with:                             │
│  - error_percentage                                     │
│  - original_english (with errors)                       │
│  - final_english (after 3-agent chain)                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 3. EMBEDDINGS CALCULATION PHASE (Automated)             │
├─────────────────────────────────────────────────────────┤
│ Run: python3 src/calculate_results.py                   │
│                                                         │
│ Produces:                                               │
│  - Console output (formatted results table)             │
│  - data/experiment_results.json                         │
│  - screenshots/translation_distance_graph.png           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 4. ANALYSIS PHASE                                       │
├─────────────────────────────────────────────────────────┤
│ Review outputs:                                         │
│  - data/experiment_results.json (machine-readable)      │
│  - data/experiment_data.md (human-readable)             │
│  - screenshots/translation_distance_graph.png           │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Running the Automated Phase

```bash
# Install dependencies
pip install sentence-transformers scikit-learn matplotlib pandas numpy

# Run embeddings calculation
python3 src/calculate_results.py

# Output files are generated automatically
```

---

## 5. Current Setup Status

### What Is Automated
- ✅ Embeddings calculation using SentenceTransformer
- ✅ Cosine distance computation
- ✅ Visualization generation (graph)
- ✅ Statistical analysis
- ✅ JSON output generation

### What Is Manual
- ⚠️ Agent invocation (18 separate Claude Code Task calls)
- ⚠️ Output collection (manual copy-paste into experiments array)
- ⚠️ Updates to calculate_results.py script

### Why Manual?
The agent invocations require:
- Human judgment on prompt engineering
- Selection of specific Claude model
- Real-time error handling and re-runs if needed
- Verification of translation quality

These steps benefit from human oversight rather than full automation.

---

## 6. To Reproduce the Experiment

### 6.1 If You Have the Results Already

Just run the embeddings calculator:
```bash
python3 src/calculate_results.py
```

This regenerates all outputs from the hardcoded experiments data.

### 6.2 If You Want to Re-Run from Scratch

1. **Create new English sentences** with desired error rates
2. **Run Agent A** 6 times (one for each error rate)
3. **Run Agent B** 6 times (one for each Agent A output)
4. **Run Agent C** 6 times (one for each Agent B output)
5. **Update** `experiments` array in `src/calculate_results.py`
6. **Run** `python3 src/calculate_results.py`

---

## 7. Data Structure

### 7.1 experiments Array Format

```python
experiments = [
    {
        "error_percentage": 0,
        "original_english": "The advanced artificial...",  # Original with errors
        "final_english": "The advanced artificial..."      # Output after 3-agent chain
    },
    # ... repeat for each error rate
]
```

### 7.2 Output: experiment_results.json

```json
[
    {
        "error_percentage": 0,
        "original_english": "...",
        "final_english": "...",
        "cosine_distance": 0.098352,
        "cosine_similarity": 0.901648
    },
    // ... 5 more entries
]
```

---

## 8. Quality Assurance

### Verification Checklist

- [ ] All 6 error rates generated (0%, 10%, 20%, 30%, 40%, 50%)
- [ ] Each error rate has 3 translation outputs (French, Hebrew, English)
- [ ] Original sentences contain correct spelling error percentages
- [ ] Final English outputs are natural and coherent
- [ ] Cosine distances increase with error rates (mostly monotonic)
- [ ] Statistics are calculated correctly
- [ ] Graph visualization displays correctly
- [ ] JSON is valid and complete

---

## 9. Key Insights from This Process

### 9.1 Why This Two-Phase Approach?

**Phase 1 (Manual)**: Requires human intelligence for:
- Prompt engineering
- Real-time error handling
- Translation quality verification
- Agent skill application

**Phase 2 (Automated)**: Handles computational tasks:
- Vector calculations
- Statistical analysis
- Visualization generation
- Batch processing

### 9.2 Design Rationale

The hardcoded experiments array was used because:
- ✅ Ensures reproducibility (same data every run)
- ✅ Simplifies the Python script (no file I/O needed)
- ✅ Makes results inspection easy (visible in code)
- ⚠️ But it's not ideal for production (would need input file support)

---

## 10. Future Improvements

If this experiment were to be scaled:

1. **Automate Agent Calls**: Use Claude API instead of manual invocation
2. **Create Input Format**: Read from `experiments_input.json` file
3. **Add CLI Arguments**: `python3 src/calculate_results.py --input file.json`
4. **Batch Processing**: Parallel agent invocation
5. **Result Caching**: Save intermediate outputs
6. **Validation**: Automated quality checks on translations

---

## References

- **Main README**: [README.md](README.md)
- **Experimental Data**: [data/experiment_data.md](data/experiment_data.md)
- **Results JSON**: [data/experiment_results.json](data/experiment_results.json)
- **Results Script**: [src/calculate_results.py](src/calculate_results.py)
- **Agent A**: [docs/agent_a_english_to_french.md](docs/agent_a_english_to_french.md)
- **Agent B**: [docs/agent_b_french_to_hebrew.md](docs/agent_b_french_to_hebrew.md)
- **Agent C**: [docs/agent_c_hebrew_to_english.md](docs/agent_c_hebrew_to_english.md)

---

**Document Version**: 1.0
**Last Updated**: November 14, 2025
**Status**: Complete
