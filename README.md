# LLM Translation Agents Pipeline

A multi-agent system that performs sequential translation (English → French → Hebrew → English) to analyze how spelling errors propagate through LLM-based translation chains.

## Overview

This project simulates a "Turing Machine" using three LLM agents to study:
- How LLM agents handle spelling errors in input
- Error propagation through translation chains
- Semantic degradation measured by vector distance

**Architecture:** Three sequential agents, each performing a translation step, with varying levels of spelling errors (0%, 10%, 20%, 30%, 40%, 50%).

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [System Prompts](#system-prompts)
- [Configuration](#configuration)
- [Running Experiments](#running-experiments)
- [Results & Analysis](#results--analysis)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

```bash
# 1. Clone and navigate to project
cd llm-translation-agents-pipeline

# 2. Set up environment
cp config/.env.example config/.env
# Edit config/.env with your API keys

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run a quick test
python src/run_embeddings_test.py

# 5. See documentation
cat docs/README_AGENTS.md
```

## Installation

### Prerequisites

- **Python:** 3.8 or higher
- **API Access:** OpenAI API key OR Anthropic Claude API key
- **CLI:** OpenAI CLI or Claude Code CLI installed
- **Git:** For version control

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd llm-translation-agents-pipeline
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Required packages:
- `openai >= 1.0.0` - OpenAI API client
- `numpy >= 1.21.0` - Numerical computing
- `scipy >= 1.7.0` - Scientific computing (for cosine distance)
- `pandas >= 1.3.0` - Data manipulation
- `matplotlib >= 3.4.0` - Visualization
- `jupyter >= 1.0.0` - Jupyter notebook support
- `python-dotenv >= 0.19.0` - Environment variable management
- `pyyaml >= 5.4.0` - Configuration file support

#### 4. Configure Environment Variables

```bash
# Copy the example configuration
cp config/.env.example config/.env

# Edit config/.env with your settings
# Required:
# - OPENAI_API_KEY=sk-... (or CLAUDE_API_KEY=...)
# - EMBEDDING_MODEL=text-embedding-3-small
# - LLM_MODEL=gpt-4-turbo (or claude-3-opus-20240229)

nano config/.env  # or use your preferred editor
```

**Important:** Never commit `.env` file with real API keys. It's in `.gitignore`.

#### 5. Verify Installation

```bash
# Test embeddings function
python src/embeddings_calculator.py --test

# Test configuration
python -c "from src.config_loader import load_config; print(load_config())"
```

## Project Structure

```
llm-translation-agents-pipeline/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── config/                            # Configuration files
│   ├── .env.example                  # Example environment configuration
│   ├── agent_prompts.yaml            # System prompts for 3 agents
│   └── experiment_config.json        # Experiment parameters
│
├── src/                              # Source code
│   ├── embeddings_calculator.py      # Calculate embeddings & distance
│   ├── config_loader.py              # Load configuration
│   ├── error_injector.py             # Inject spelling errors
│   └── results_aggregator.py         # Aggregate results
│
├── data/                             # Test data
│   ├── test_sentences.json           # Original test sentences
│   └── test_sentences_with_errors/   # Sentences with error injection
│       ├── 0_percent.txt
│       ├── 10_percent.txt
│       ├── 20_percent.txt
│       ├── 30_percent.txt
│       ├── 40_percent.txt
│       └── 50_percent.txt
│
├── results/                          # Experiment results
│   ├── translations/                 # All translation outputs
│   │   ├── agent_a_outputs.json
│   │   ├── agent_b_outputs.json
│   │   └── agent_c_outputs.json
│   ├── analysis/                     # Analysis outputs
│   │   ├── experiment_results.json
│   │   ├── results_summary.csv
│   │   └── statistics.json
│   └── graphs/                       # Visualization outputs
│       ├── error_vs_distance.png
│       ├── error_vs_distance.svg
│       └── detailed_analysis.png
│
├── notebooks/                        # Jupyter notebooks
│   └── analysis.ipynb               # Complete analysis notebook
│
├── docs/                            # Documentation
│   ├── PRD.md                       # Product Requirements Document
│   ├── ARCHITECTURE.md              # System architecture
│   ├── README_AGENTS.md             # Detailed agent descriptions
│   └── COST_ANALYSIS.md             # Token usage & cost breakdown
│
└── tests/                           # Unit tests
    ├── test_embeddings.py
    ├── test_error_injector.py
    └── test_distance_calculation.py
```

## Usage

### 1. Preparing Test Data

#### Option A: Using Provided Test Sentences

The project includes pre-configured test sentences. View them:

```bash
cat data/test_sentences.json
```

#### Option B: Adding Your Own Sentences

Edit `data/test_sentences.json`:

```json
{
  "sentences": [
    {
      "id": "sent_1",
      "original": "The quick brown fox jumps over the lazy dog in the sunny afternoon with great enthusiasm and perfect accuracy.",
      "notes": "Natural sentence, 17 words"
    }
  ]
}
```

**Requirements:**
- Minimum 15 words per sentence
- Clear, meaningful English text
- Can include multiple sentences

### 2. Injecting Spelling Errors

Automatically generate test data with errors:

```bash
python src/error_injector.py \
  --input data/test_sentences.json \
  --error-rates 0 10 20 30 40 50 \
  --output data/test_sentences_with_errors/
```

This creates 6 files (one per error rate) with random word misspellings.

### 3. Running Individual Agents via CLI

#### Agent A: English → French

```bash
# Using Claude Code CLI
claude-code --prompt "You are a professional English-to-French translator. \
Translate the following text to French, handling any spelling errors gracefully: \
'${INPUT_TEXT}'"

# Using OpenAI CLI
openai api chat.completions.create \
  -m gpt-4-turbo \
  -n 1 \
  "Translate to French: ${INPUT_TEXT}"
```

**Save the output:**
```bash
# Example using bash
INPUT="The quick brown fox jumps over the lazy dog"
AGENT_A_OUTPUT=$(claude-code --prompt "Translate to French: $INPUT")
echo "$AGENT_A_OUTPUT" > results/translations/agent_a_output_0pct.txt
```

#### Agent B: French → Hebrew

```bash
# Continue with Agent A output
AGENT_B_OUTPUT=$(claude-code --prompt "Translate to Hebrew: $AGENT_A_OUTPUT")
echo "$AGENT_B_OUTPUT" > results/translations/agent_b_output_0pct.txt
```

#### Agent C: Hebrew → English

```bash
# Final step
AGENT_C_OUTPUT=$(claude-code --prompt "Translate to English: $AGENT_B_OUTPUT")
echo "$AGENT_C_OUTPUT" > results/translations/agent_c_output_0pct.txt
```

### 4. Batch Processing with Scripts

Run all three agents sequentially (recommended):

```bash
# Manual workflow script
bash scripts/run_full_pipeline.sh \
  --error-rate 0 \
  --input-sentence "The quick brown fox jumps over the lazy dog in the sunny afternoon"
```

**Script workflow:**
1. Take input sentence with specific error rate
2. Run through Agent A (ENG → FRA)
3. Pass output to Agent B (FRA → HE)
4. Pass output to Agent C (HE → ENG)
5. Log all intermediates

### 5. Calculate Embeddings & Distance

After collecting all translations, calculate vector distances:

```bash
# Run embeddings calculation
python src/embeddings_calculator.py \
  --translations results/translations_log.json \
  --output results/analysis/

# Optional: specify model
python src/embeddings_calculator.py \
  --translations results/translations_log.json \
  --model text-embedding-3-small \
  --output results/analysis/
```

**Output:**
```json
{
  "error_rate": 0,
  "original_sentence": "...",
  "final_sentence": "...",
  "cosine_similarity": 0.95,
  "cosine_distance": 0.05,
  "embedding_dimensions": 1536
}
```

### 6. Generate Visualizations

Create graphs showing error rate vs. vector distance:

```bash
python src/visualizer.py \
  --results results/analysis/experiment_results.json \
  --output results/graphs/
```

**Outputs:**
- `error_vs_distance.png` - Line plot with scatter points
- `error_vs_distance.svg` - Vector format for printing
- `detailed_analysis.png` - Multi-panel analysis

## System Prompts

### Agent A: English → French Translator

**Role:** Translate English text to French, handling spelling errors gracefully

**System Prompt:**
```
You are a professional English-to-French translator with expertise in handling
noisy or corrupted text. Your task is to translate English text into French.

Instructions:
1. Translate accurately while preserving meaning and nuance
2. Handle spelling errors gracefully - infer intended words from context
3. Maintain natural, idiomatic French phrasing
4. If uncertain, provide your best interpretation

Output ONLY the French translation, no explanations.
```

See `docs/README_AGENTS.md` for complete prompt specifications.

### Agent B: French → Hebrew Translator

**Role:** Translate French text to Hebrew

**System Prompt:**
```
You are a professional French-to-Hebrew translator. Your task is to translate
the provided French text into Hebrew.

Instructions:
1. Translate accurately, preserving the original meaning
2. Use natural, idiomatic Hebrew
3. Handle any language quirks from the source text
4. Maintain proper grammar and sentence structure

Output ONLY the Hebrew translation, no explanations.
```

See `docs/README_AGENTS.md` for complete prompt specifications.

### Agent C: Hebrew → English Translator

**Role:** Translate Hebrew text back to English

**System Prompt:**
```
You are a professional Hebrew-to-English translator. Your task is to back-translate
the provided Hebrew text into English.

Instructions:
1. Translate accurately to natural English
2. Preserve the meaning and context
3. Use proper English grammar and phrasing
4. Provide a fluent, natural translation

Output ONLY the English translation, no explanations.
```

See `docs/README_AGENTS.md` for complete prompt specifications.

## Configuration

### Environment Variables

Create `config/.env`:

```bash
# API Configuration
OPENAI_API_KEY=sk-your-key-here
CLAUDE_API_KEY=sk-your-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# Model Configuration
LLM_MODEL=gpt-4-turbo
EMBEDDING_MODEL=text-embedding-3-small

# Experiment Configuration
ERROR_RATES=0,10,20,30,40,50
TEST_BATCH_SIZE=1
TIMEOUT_SECONDS=60

# Output Configuration
OUTPUT_DIR=results/
LOG_LEVEL=INFO
```

### Agent Prompts Configuration

Edit `config/agent_prompts.yaml`:

```yaml
agents:
  agent_a:
    name: "English to French Translator"
    language_pair: "en_to_fr"
    system_prompt: "You are a professional..."
    model_override: "gpt-4-turbo"
    temperature: 0.3

  agent_b:
    name: "French to Hebrew Translator"
    language_pair: "fr_to_he"
    system_prompt: "You are a professional..."
    model_override: null
    temperature: 0.3

  agent_c:
    name: "Hebrew to English Translator"
    language_pair: "he_to_en"
    system_prompt: "You are a professional..."
    model_override: null
    temperature: 0.3

embeddings:
  model: "text-embedding-3-small"
  dimensions: 1536
```

## Running Experiments

### Complete Workflow

```bash
# 1. Set up
source venv/bin/activate
cd llm-translation-agents-pipeline

# 2. Prepare test data with errors
python src/error_injector.py \
  --input data/test_sentences.json \
  --error-rates 0 10 20 30 40 50

# 3. For each error rate, run agents (Manual or via script)
# Option A: Using provided bash script
bash scripts/run_full_pipeline.sh

# Option B: Manual execution
# ... run three agents via CLI as shown above ...
# ... collect outputs in results/translations/ ...

# 4. Calculate embeddings and distances
python src/embeddings_calculator.py \
  --translations results/translations_log.json \
  --output results/analysis/

# 5. Generate visualizations
python src/visualizer.py \
  --results results/analysis/experiment_results.json \
  --output results/graphs/

# 6. Create analysis notebook
jupyter notebook notebooks/analysis.ipynb
```

### Expected Execution Time

| Step | Time |
|------|------|
| Error injection | < 1 minute |
| Agent A (6 calls) | ~15-30 minutes |
| Agent B (6 calls) | ~15-30 minutes |
| Agent C (6 calls) | ~15-30 minutes |
| Embeddings calculation | < 1 minute |
| Visualization | < 1 minute |
| **Total** | **~1-2 hours** |

## Results & Analysis

### Experiment Results Table

Located in `results/analysis/results_summary.csv`:

```csv
error_rate,original_sentence,final_sentence,cosine_similarity,cosine_distance,tokens_used
0%,"The quick brown...",The quick brown...",0.95,0.05,1234
10%,"The quikc brown...",The quick brown with...",0.87,0.13,1456
20%,"The quikc brwon...",The quick brown but...",0.78,0.22,1512
...
50%,"The qukc brwn...","The rapid brown creature...",0.42,0.58,2100
```

### Visualizations

- **error_vs_distance.png:** Primary graph showing error rate vs. cosine distance
- **detailed_analysis.png:** Additional metrics and correlations

### Analysis Notebook

Open `notebooks/analysis.ipynb` to see:
- Data loading and preprocessing
- Statistical analysis
- Trend identification
- Conclusions and insights

```bash
jupyter notebook notebooks/analysis.ipynb
```

## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test OpenAI connection
python -c "from openai import OpenAI; print('OK')"

# Test Claude connection
python -c "from anthropic import Anthropic; print('OK')"
```

### Embedding Calculation Errors

```bash
# Check input file format
cat results/translations_log.json | head -20

# Run with verbose logging
python src/embeddings_calculator.py \
  --translations results/translations_log.json \
  --output results/analysis/ \
  --verbose
```

### Memory/Rate Limiting

```bash
# Reduce batch size
python src/embeddings_calculator.py \
  --batch-size 2 \
  --delay-seconds 1

# Use smaller embedding model
EMBEDDING_MODEL=text-embedding-3-small python src/embeddings_calculator.py
```

## Contributing

To extend or modify the project:

1. **Add new agents:** Edit `config/agent_prompts.yaml`
2. **Change error injection:** Modify `src/error_injector.py`
3. **Add analysis:** Create new Jupyter notebooks in `notebooks/`
4. **Extend visualization:** Modify `src/visualizer.py`

## License

This project is part of an academic assignment. All code and documentation are provided as-is.

## Documentation Reference

- **PRD:** `docs/PRD.md` - Complete requirements and success criteria
- **Architecture:** `docs/ARCHITECTURE.md` - System design and data flow
- **Agent Details:** `docs/README_AGENTS.md` - Full prompt specifications
- **Cost Analysis:** `docs/COST_ANALYSIS.md` - Token usage and expenses

## Support

For issues or questions:
1. Check this README's Troubleshooting section
2. Review `docs/README_AGENTS.md` for agent-specific issues
3. Check `docs/ARCHITECTURE.md` for system design questions
4. Review `notebooks/analysis.ipynb` for analysis examples

---

**Last Updated:** November 14, 2024
**Version:** 1.0.0
**Author:** Assignment 3 - LLM Agents Course
