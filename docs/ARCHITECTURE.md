# Architecture Documentation
## LLM Translation Agents Pipeline

### 1. System Overview

This document describes the architecture of the LLM Translation Agents Pipeline system that performs multi-step translation with error propagation analysis.

### 2. C4 Model - System Context

```
┌─────────────────────────────────────────────────────────────┐
│                   External Systems                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Claude API  │  │  OpenAI API  │  │ Embeddings   │    │
│  │  (Agents)    │  │  (Optional)  │  │ Service      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                 │             │
│         └──────────────────┼─────────────────┘             │
│                            │                               │
│                    ┌───────▼────────┐                      │
│                    │ LLM Translation│                      │
│                    │  Pipeline      │                      │
│                    │   System       │                      │
│                    └────────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3. C4 Model - Container Diagram

```
┌────────────────────────────────────────────────────────────────┐
│           LLM Translation Pipeline System                      │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                                          │
│  │ CLI Commands     │  (Agent Execution Interface)            │
│  │ & Scripts        │                                          │
│  └────────┬─────────┘                                          │
│           │                                                    │
│  ┌────────▼──────────────────────────────────────────────┐   │
│  │        Agent Orchestration Layer                      │   │
│  │  • Agent A: English → French                          │   │
│  │  • Agent B: French → Hebrew                           │   │
│  │  • Agent C: Hebrew → English                          │   │
│  │  • Configuration & Prompts                            │   │
│  └────────┬──────────────────────────────────────────────┘   │
│           │                                                    │
│  ┌────────▼──────────────────────────────────────────────┐   │
│  │      Data Management Layer                            │   │
│  │  • Test Data (sentences with error injection)         │   │
│  │  • Translation Outputs (all intermediate steps)       │   │
│  │  • Results Database (experiment outcomes)             │   │
│  └────────┬──────────────────────────────────────────────┘   │
│           │                                                    │
│  ┌────────▼──────────────────────────────────────────────┐   │
│  │      Analysis & Visualization Layer                   │   │
│  │  • Embeddings Calculation (Python)                    │   │
│  │  • Vector Distance Measurement                        │   │
│  │  • Results Aggregation                                │   │
│  │  • Graph Generation                                   │   │
│  │  • Analysis Notebook                                  │   │
│  └────────┬──────────────────────────────────────────────┘   │
│           │                                                    │
│  ┌────────▼──────────────────────────────────────────────┐   │
│  │      Output & Reporting                               │   │
│  │  • Experiment Results Table                           │   │
│  │  • Visualizations (PNG/SVG)                           │   │
│  │  • Analysis Report (Jupyter Notebook)                 │   │
│  │  • Documentation                                       │   │
│  └────────┬──────────────────────────────────────────────┘   │
│           │                                                    │
└───────────┼────────────────────────────────────────────────────┘
            │
    ┌───────▼──────────┐
    │   File System    │
    │   (results/)     │
    └──────────────────┘
```

### 4. Component Architecture

#### 4.1 Agent Orchestration Layer

**Purpose:** Execute LLM agents in sequence via CLI

**Components:**

1. **Agent A: English → French**
   - Input: English text with spelling errors
   - System Prompt: Focuses on translation accuracy, error robustness
   - Output: French translation
   - CLI Command: `claude-code` with specific prompt injection

2. **Agent B: French → Hebrew**
   - Input: French translation from Agent A
   - System Prompt: French-to-Hebrew translation specialist
   - Output: Hebrew translation
   - CLI Command: `claude-code` or `openai` with specific prompt

3. **Agent C: Hebrew → English**
   - Input: Hebrew translation from Agent B
   - System Prompt: Hebrew-to-English translation specialist
   - Output: English translation (for final comparison)
   - CLI Command: `claude-code` or `openai` with specific prompt

**Data Flow:**
```
Original Text (ENG)
       ↓
   Agent A
       ↓
Intermediate (FRA)
       ↓
   Agent B
       ↓
Intermediate (HE)
       ↓
   Agent C
       ↓
Final Text (ENG)
```

#### 4.2 Data Management Layer

**Purpose:** Handle test data generation and results storage

**Components:**

1. **Test Data Generation**
   - Base sentence: ≥15 words in English
   - Error injection: 0%, 10%, 20%, 30%, 40%, 50% spelling errors
   - Random word selection for error introduction
   - Storage: `data/test_sentences.json`

2. **Translation Outputs Storage**
   - Each error rate → 4 versions (Original, Intermediate FRA, Intermediate HE, Final ENG)
   - Metadata: timestamps, error rate, agent info
   - Storage: `results/translations_log.json`

3. **Experiment Results Database**
   - Vector distances for each error rate
   - Token usage tracking (for cost analysis)
   - Metadata: model names, embedding dimensions
   - Storage: `results/experiment_results.json`

#### 4.3 Analysis & Visualization Layer

**Purpose:** Calculate metrics and generate insights

**Components:**

1. **Embeddings Calculator** (Python)
   - Input: Original and final sentences
   - Model: OpenAI embeddings (text-embedding-3-small or similar)
   - Output: Embedding vectors (1536-dim default)
   - Function: `calculate_embeddings(text_list) → List[List[float]]`

2. **Distance Measurement** (Python)
   - Input: Two embedding vectors
   - Formula: `cosine_distance = 1 - cosine_similarity`
   - scipy.spatial.distance.cosine()
   - Output: Single float (0.0-2.0 range)

3. **Results Aggregation** (Python)
   - Correlate error rates with vector distances
   - Calculate statistics (mean, std, correlation coefficient)
   - Generate summary table
   - Storage: `results/analysis_summary.csv`

4. **Visualization** (Python)
   - Library: matplotlib, pandas
   - Graph Type: Line plot with scatter points
   - X-axis: Error Rate (0%, 10%, 20%, 30%, 40%, 50%)
   - Y-axis: Cosine Distance
   - Output: PNG/SVG in `results/graphs/`

### 5. Data Flow Diagram

```
┌─────────────────────┐
│ Test Sentences      │
│ (6 error rates)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Agent A             │  CLI Execution
│ (ENG → FRA)         │  (Claude Code)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Agent B             │  CLI Execution
│ (FRA → HE)          │  (Claude Code)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Agent C             │  CLI Execution
│ (HE → ENG)          │  (Claude Code)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Results Collection  │  Manual + Script
│ (All translations)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Python Script       │
│ Embeddings + Distance
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Results Table &     │
│ Visualization       │
└─────────────────────┘
```

### 6. Operational Architecture

#### 6.1 Execution Workflow

```
Day 1-2: Setup & Configuration
  ├─ Set up project structure
  ├─ Configure API keys (.env)
  ├─ Design system prompts for each agent
  └─ Prepare test data with error injection

Day 3-4: Agent Execution
  ├─ For each error rate (0%, 10%, ..., 50%):
  │  ├─ Run Agent A via CLI (record output)
  │  ├─ Run Agent B via CLI (record output)
  │  └─ Run Agent C via CLI (record output)
  └─ Consolidate all outputs to results/

Day 5: Analysis
  ├─ Load all translations
  ├─ Calculate embeddings (Python)
  ├─ Measure vector distances
  ├─ Create results table
  ├─ Generate graph
  └─ Write analysis notebook

Day 6-7: Documentation & Submission
  ├─ Finalize all documentation
  ├─ Complete self-evaluation
  ├─ Review for quality
  └─ Submit artifacts
```

#### 6.2 Configuration Management

**Configuration Files:**
- `.env` - API keys, model names
- `config/agent_prompts.yaml` - System prompts for each agent
- `config/experiment_config.json` - Test parameters, error rates

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo
```

### 7. Quality Attributes

#### 7.1 Performance
- Each agent execution: <60 seconds (typical)
- Embeddings calculation: <5 seconds per batch
- Full experiment: 1-2 hours total

#### 7.2 Reliability
- All outputs logged and persisted
- Error handling for API failures
- Graceful degradation (fallback models available)

#### 7.3 Maintainability
- Modular agent design (each in separate prompt file)
- Configuration-driven (easy to modify prompts)
- Well-documented workflows
- Version control for all artifacts

#### 7.4 Testability
- Unit tests for distance calculation
- Integration tests for full pipeline
- Manual verification of outputs

### 8. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| CLI-only for agents | Requirement specified; ensures no hidden logic in Python |
| Python for embeddings only | Clean separation: AI execution vs. ML analysis |
| Three sequential agents | Simulates Turing Machine with information loss/degradation |
| 6 error rates | Provides adequate data points for trend analysis |
| Cosine distance metric | Standard for semantic similarity; interpretable (0-2 range) |
| Jupyter notebook for analysis | Interactive, reproducible, presentation-ready format |

### 9. Extension Points

1. **Add More Languages:** Extend the agent chain (e.g., English → French → German → Chinese → English)
2. **Add More LLM Models:** Compare translation quality across different models
3. **Advanced Error Injection:** Non-random errors (phonetic, semantic, syntactic)
4. **Real-time Visualization:** Create web dashboard for interactive exploration
5. **Statistical Analysis:** Add hypothesis testing for error rate correlations

### 10. Technology Stack

- **Language Specification:** Markdown (documentation), JSON (config/data), Python 3.9+
- **LLM Interfaces:** OpenAI API, Claude API
- **Python Libraries:**
  - openai, anthropic (API clients)
  - numpy, scipy (mathematical operations)
  - pandas (data manipulation)
  - matplotlib, seaborn (visualization)
  - jupyter (notebooks)
- **Version Control:** Git
- **Testing:** pytest (for Python modules)
