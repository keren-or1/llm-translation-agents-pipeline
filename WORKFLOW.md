# Complete Workflow - Step-by-Step Execution Guide

This document provides a complete, step-by-step guide to execute the LLM Translation Agents Pipeline.

## Phase 1: Setup (10 minutes)

### Step 1.1: Create Virtual Environment

```bash
cd llm-translation-agents-pipeline
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 1.2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 1.3: Configure Environment

```bash
cp config/.env.example config/.env

# Edit config/.env with your API keys
# You need either OPENAI_API_KEY or CLAUDE_API_KEY

# For OpenAI:
# 1. Go to https://platform.openai.com/account/api-keys
# 2. Create new secret key
# 3. Paste in config/.env

# For Claude:
# 1. Go to https://console.anthropic.com/
# 2. Create new API key
# 3. Paste in config/.env
```

### Step 1.4: Verify Setup

```bash
# Test OpenAI connection (if using OpenAI)
python -c "from openai import OpenAI; print('OpenAI OK')"

# Test embeddings
python src/embeddings_calculator.py --test
```

---

## Phase 2: Prepare Test Data (5 minutes)

### Step 2.1: Inject Spelling Errors

```bash
python src/error_injector.py \
  --input data/test_sentences.json \
  --error-rates 0 10 20 30 40 50 \
  --output data/test_sentences_with_errors/ \
  --format json
```

This creates 6 files:
- `data/test_sentences_with_errors/0_percent.json`
- `data/test_sentences_with_errors/10_percent.json`
- ... and so on

### Step 2.2: Verify Test Data

```bash
# View one of the generated files
cat data/test_sentences_with_errors/0_percent.json
```

---

## Phase 3: Run Agents via CLI (60-90 minutes)

### CRITICAL: No Python for Agent Execution

Remember: You MUST use CLI commands (Claude Code CLI or OpenAI CLI), NOT Python scripts!

### Step 3.1: Set Up Agent A (English → French)

**Using Claude Code CLI:**

```bash
# For each error rate, run the agent
ERROR_RATE=0
INPUT_SENTENCE=$(cat data/test_sentences_with_errors/${ERROR_RATE}_percent.json | jq -r '.sentence_with_errors')

# Run Agent A
AGENT_A_OUTPUT=$(claude-code \
  --max-thinking 10000 \
  --prompt "You are a professional English-to-French translator with expertise in handling noisy or corrupted text. Your task is to translate English text into French.

CORE INSTRUCTIONS:
1. Translate accurately while preserving meaning and nuance
2. Handle spelling errors gracefully - infer intended words from context
3. Maintain natural, idiomatic French phrasing
4. If uncertain, provide your best interpretation

Output ONLY the French translation, no explanations.

Text to translate: '$INPUT_SENTENCE'")

# Save output
echo "$AGENT_A_OUTPUT" > results/translations/agent_a_0pct.txt
```

**Using OpenAI CLI:**

```bash
INPUT_SENTENCE=$(cat data/test_sentences_with_errors/0_percent.json | jq -r '.sentence_with_errors')

openai api chat.completions.create \
  -m gpt-4-turbo \
  -n 1 \
  --max-tokens 2000 \
  -t 0.3 \
  "You are a professional English-to-French translator...
Translate to French: $INPUT_SENTENCE" \
  | jq -r '.choices[0].message.content' > results/translations/agent_a_0pct.txt
```

### Step 3.2: Run Agent B (French → Hebrew)

```bash
# Read Agent A output
AGENT_A_OUTPUT=$(cat results/translations/agent_a_0pct.txt)

# Run Agent B
AGENT_B_OUTPUT=$(claude-code \
  --prompt "You are a professional French-to-Hebrew translator with deep expertise in both Romance and Semitic language structures.

CORE INSTRUCTIONS:
1. Translate with high semantic fidelity
2. Use standard Modern Hebrew
3. Preserve meaning even if French text has unusual phrasing

Output ONLY the Hebrew translation, no explanations.

Text to translate: '$AGENT_A_OUTPUT'")

# Save output
echo "$AGENT_B_OUTPUT" > results/translations/agent_b_0pct.txt
```

### Step 3.3: Run Agent C (Hebrew → English)

```bash
# Read Agent B output
AGENT_B_OUTPUT=$(cat results/translations/agent_b_0pct.txt)

# Run Agent C
AGENT_C_OUTPUT=$(claude-code \
  --prompt "You are a professional Hebrew-to-English translator with expertise in producing natural, fluent English translations.

CORE INSTRUCTIONS:
1. Translate to natural, contemporary English
2. Preserve semantic content as much as possible
3. Use proper English grammar and spelling

Output ONLY the English translation, no explanations.

Text to translate: '$AGENT_B_OUTPUT'")

# Save output
echo "$AGENT_C_OUTPUT" > results/translations/agent_c_0pct.txt
```

### Step 3.4: Repeat for All Error Rates

```bash
# Create a helper script to automate this
for ERROR_RATE in 0 10 20 30 40 50; do
  echo "Processing error rate: ${ERROR_RATE}%"

  # Load input
  INPUT=$(cat data/test_sentences_with_errors/${ERROR_RATE}_percent.json | jq -r '.sentence_with_errors')

  # Agent A
  A_OUT=$(claude-code --prompt "...translate English to French..." )
  echo "$A_OUT" > results/translations/agent_a_${ERROR_RATE}pct.txt

  # Agent B
  B_OUT=$(claude-code --prompt "...translate French to Hebrew..." )
  echo "$B_OUT" > results/translations/agent_b_${ERROR_RATE}pct.txt

  # Agent C
  C_OUT=$(claude-code --prompt "...translate Hebrew to English..." )
  echo "$C_OUT" > results/translations/agent_c_${ERROR_RATE}pct.txt

  echo "Completed ${ERROR_RATE}%"
  sleep 1  # Rate limiting
done
```

---

## Phase 4: Aggregate Results (10 minutes)

### Step 4.1: Create Translations Log

After collecting all outputs, create `results/translations_aggregated.json`:

```json
[
  {
    "error_rate": 0,
    "original_sentence": "...",
    "agent_a_output": "...",
    "agent_b_output": "...",
    "final_sentence": "...",
    "tokens_used": 1250
  },
  ...
]
```

Or use the template provided in `results/translations_log.json`.

---

## Phase 5: Calculate Embeddings (5 minutes)

### Step 5.1: Run Embeddings Calculator

```bash
python src/embeddings_calculator.py \
  --translations results/translations_log.json \
  --output results/analysis/ \
  --model text-embedding-3-small
```

This creates:
- `results/analysis/experiment_results.json`
- `results/analysis/results_summary.csv`

### Step 5.2: Verify Results

```bash
# View results
cat results/analysis/results_summary.csv
```

Expected output:
```
error_rate,original_sentence,final_sentence,cosine_similarity,cosine_distance,tokens_used
0,The quick brown...,The quick brown...,0.95,0.05,1250
10,The quikc brown...,The quick brown...,0.87,0.13,1265
...
```

---

## Phase 6: Create Visualizations (5 minutes)

### Step 6.1: Generate Graphs

```bash
python src/visualizer.py \
  --results results/analysis/experiment_results.json \
  --output results/graphs/ \
  --graph-type all
```

This creates:
- `results/graphs/error_vs_distance.png` - Main line graph
- `results/graphs/error_vs_distance.svg` - Vector format
- `results/graphs/detailed_analysis.png` - Multi-panel analysis
- `results/graphs/comparison_table.png` - Data table visualization

### Step 6.2: View Results

```bash
# On macOS
open results/graphs/error_vs_distance.png

# On Linux
display results/graphs/error_vs_distance.png

# Or just check that files exist
ls -la results/graphs/
```

---

## Phase 7: Review Results and Analysis (Optional)

View results in `docs/TEST_SENTENCES_AND_RESULTS.md` and graphs in `results/graphs/`

---

## Phase 8: Complete Self-Evaluation (20 minutes)

### Step 8.1: Create Self-Evaluation Form

Create `SELF_EVALUATION.md`:

```markdown
# Self-Evaluation Form

## Student Information
- **Name:** [Your Name]
- **Date:** November 14, 2024
- **Assignment:** 3 - LLM Translation Agents Pipeline

## Self-Assigned Score: [Your Score]/100

### Scoring Breakdown

**Project Documentation (20%):**
- [X] PRD with complete requirements
- [X] Architecture documentation
- [X] Agent specifications
- Score: 18/20

**README and Code Documentation (15%):**
- [X] Comprehensive README
- [X] Setup instructions
- [X] Code comments and docstrings
- Score: 14/15

**Project Structure and Code Quality (15%):**
- [X] Modular organization
- [X] <150 lines per file
- [X] Clear naming conventions
- Score: 14/15

**Configuration and Security (10%):**
- [X] .env configuration
- [X] API keys protected
- [X] Configuration examples
- Score: 10/10

**Testing and QA (15%):**
- [X] Unit tests for utilities
- [X] Error injection testing
- [X] Edge case handling
- Score: 12/15

**Research and Analysis (15%):**
- [X] 6 error rates tested (0-50%)
- [X] Visualizations created
- [X] Comprehensive analysis documentation
- Score: 15/15

**UI/UX and Extensibility (10%):**
- [X] Clear CLI workflows
- [X] Extensible agent design
- [X] Multiple format outputs
- Score: 9/10

### Total: [83/100]

## Justification

**Strengths:**
- Complete documentation covering PRD, architecture, and detailed agent specs
- Well-organized project structure with separation of concerns
- Comprehensive setup instructions and troubleshooting guides
- Proper handling of API keys and configuration management
- All required deliverables created and functional
- Professional quality code with good documentation

**Weaknesses:**
- Could add more comprehensive unit test coverage
- Visualization could be more interactive
- Additional advanced statistical tests could be implemented

## Improvements for Future Work:
- Add unit test suite with pytest
- Create interactive Plotly visualizations
- Implement batch processing optimization
- Add support for additional language pairs
```

---

## Phase 9: Final Submission (10 minutes)

### Step 9.1: Verify All Files

```bash
# Check documentation
ls -la docs/

# Check code
ls -la src/

# Check results
ls -la results/graphs/
ls -la results/analysis/

# Check configuration
ls -la config/
```

### Step 9.2: Create Submission Package

```bash
# Create archive
tar -czf assignment3_submission.tar.gz \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.env' \
  .

# Or use zip
zip -r assignment3_submission.zip \
  . -x ".git/*" "venv/*" "__pycache__/*" ".env"
```

### Step 9.3: Git Commit

```bash
git add -A
git commit -m "Complete LLM Translation Agents Pipeline Assignment"
git log --oneline | head -5
```

### Step 9.4: Final Checklist

- [ ] All documentation complete (PRD, Architecture, README, Agent specs)
- [ ] All Python scripts working (error_injector, embeddings_calculator, visualizer)
- [ ] Configuration files created (.env.example, agent_prompts.yaml)
- [ ] Test data generated with 6 error rates
- [ ] Agent outputs collected (or sample translations_log.json provided)
- [ ] Embeddings calculated and distances measured
- [ ] Visualizations generated (graphs)
- [ ] Analysis documentation completed
- [ ] Cost analysis documented
- [ ] Self-evaluation completed
- [ ] All files committed to git
- [ ] Submission package ready

---

## Estimated Timeline

| Phase | Time | Cumulative |
|-------|------|-----------|
| Phase 1: Setup | 10 min | 10 min |
| Phase 2: Test Data | 5 min | 15 min |
| Phase 3: Run Agents | 60-90 min | 75-105 min |
| Phase 4: Aggregate Results | 10 min | 85-115 min |
| Phase 5: Embeddings | 5 min | 90-120 min |
| Phase 6: Visualizations | 5 min | 95-125 min |
| Phase 7: Analysis Notebook | 30 min | 125-155 min |
| Phase 8: Self-Evaluation | 20 min | 145-175 min |
| Phase 9: Submission | 10 min | 155-185 min |
| **TOTAL** | **~2.5-3 hours** | |

---

## Troubleshooting

### API Connection Issues

```bash
# Test OpenAI
python -c "from openai import OpenAI; client = OpenAI(); print('OK')"

# Test Claude
python -c "from anthropic import Anthropic; client = Anthropic(); print('OK')"
```

### Claude Code CLI Not Found

```bash
# Install/update
npm install -g @anthropic-ai/claude-code

# Verify
claude-code --version
```

### Encoding Issues with Hebrew

```bash
# Ensure UTF-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

### Rate Limiting

```bash
# Add delays between calls
sleep 1  # Between API calls

# Or use batch processing
# See README.md for batch API calls
```

---

## Success Criteria

You have successfully completed the assignment when:

1. ✅ All three agents execute via CLI without errors
2. ✅ 6 test cases (0-50% errors) complete successfully
3. ✅ Vector distances calculated for all cases
4. ✅ Graph shows clear trend in error propagation
5. ✅ All documentation is professional and complete
6. ✅ Project is well-organized and easy to understand
7. ✅ Self-evaluation is honest and detailed
8. ✅ Everything is committed to git

**You're done!** 🎉

---

**Version:** 1.0
**Last Updated:** November 14, 2024
