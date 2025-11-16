# Product Requirements Document (PRD)
## LLM Translation Agents Pipeline - Spelling Error Propagation Analysis

### 1. Project Overview

This project simulates a multi-agent Turing Machine using three LLM agents that perform sequential translations: **English → French → Hebrew → English**. The system examines how spelling errors in the original English text propagate and accumulate through the translation chain, and measures the semantic distance between the original and final outputs.

### 2. Problem Statement

**User Need:** Understanding how LLM agents handle noisy/corrupted input (spelling errors) and how errors propagate through sequential AI processing pipelines.

**Research Question:** How does the percentage of spelling errors in the initial English sentence affect the final translation quality, measured by vector distance between original and final outputs?

### 3. Project Goals & Success Metrics (KPIs)

| Metric | Target | Success Criteria |
|--------|--------|------------------|
| Spell Error Handling | 0-50% error rates | Accurately process sentences with varying corruption levels |
| Translation Accuracy | Document outputs | Provide clear visibility into each translation step |
| Vector Distance Measurement | 6 data points (0%, 10%, 20%, 30%, 40%, 50% errors) | Calculate cosine distance for each error rate |
| Semantic Analysis | Correlation analysis | Identify trends in error propagation |
| Reproducibility | CLI-based execution | Fully document agent configurations and prompts |

### 4. Functional Requirements

#### 4.1 Agent 1: English → French Translation
- **Role:** Translate English text (with potential spelling errors) to French
- **Input:** English sentence with ≥15 words and variable spelling errors
- **Output:** French translation
- **System Prompt:** Specialized for translation and error robustness
- **Key Skill:** Handle misspelled words intelligently, preserve meaning

#### 4.2 Agent 2: French → Hebrew Translation
- **Role:** Translate French output to Hebrew
- **Input:** French output from Agent 1
- **Output:** Hebrew translation
- **System Prompt:** Specialized for French-Hebrew translation
- **Key Skill:** Maintain semantic meaning from French source

#### 4.3 Agent 3: Hebrew → English Translation
- **Role:** Back-translate Hebrew to English
- **Input:** Hebrew output from Agent 2
- **Output:** English translation (for comparison with original)
- **System Prompt:** Specialized for Hebrew-English translation
- **Key Skill:** Produce natural English output

#### 4.4 Embeddings & Distance Calculation
- **Functionality:** Calculate vector embeddings for original and final sentences
- **Metric:** Cosine distance = 1 - cosine similarity
- **Constraint:** Python-only usage (no Python for agent execution)

### 5. Non-Functional Requirements

#### 5.1 Performance & Reliability
- Agents must process input without manual pre-corrections
- All translations must complete successfully regardless of spelling error percentage
- System must gracefully handle edge cases (low semantic meaning, highly corrupted input)

#### 5.2 Scalability
- Support sentences up to 50+ words
- Handle batch processing of multiple test cases
- Support extensibility for additional error rate testing

#### 5.3 Usability & Documentation
- Clear CLI commands for running agents
- Comprehensive documentation of system prompts
- Step-by-step instructions for reproducing experiments

#### 5.4 Quality & Correctness
- 70%+ code coverage for Python modules
- Reproducible results through detailed logging
- Version-controlled experiment configurations

### 6. Scope & Constraints

#### 6.1 In Scope
- Three LLM agents (Agent A, B, C) with custom system prompts
- Testing with 6 error rate levels (0%, 10%, 20%, 30%, 40%, 50%)
- Embeddings calculation for all test cases
- Graphical visualization of results
- Comprehensive analysis and findings
- Full documentation and self-evaluation

#### 6.2 Out of Scope
- Real-time deployment of agents
- Multi-language support beyond ENG→FR→HE→ENG
- Interactive UI (CLI/output files only)
- Advanced prompt optimization techniques
- Comparison with other translation models

#### 6.3 Constraints
- **CLI-Only Agent Execution:** Must use Claude Code CLI or OpenAI CLI (NO Python code to run agents)
- **Python Usage:** Only for embeddings calculation and vector distance measurement
- **Input Requirements:** ≥15 words per sentence, ≥20% spelling errors for main test
- **No Manual Corrections:** Sentences must pass through agents as-is

### 7. Test Cases & Success Criteria

| Error Rate | Test Input | Expected Output | Success Criteria |
|------------|-----------|-----------------|-----------------|
| 0% | Original sentence (no errors) | Clean translation | Baseline - highest similarity |
| 10% | 10% words with spelling errors | Degraded translation | Measurable distance increase |
| 20% | 20% words with spelling errors | Further degradation | Continued distance increase |
| 30% | 30% words with spelling errors | Notable errors visible | Significant distance |
| 40% | 40% words with spelling errors | Major degradation | High distance expected |
| 50% | 50% words with spelling errors | Heavy corruption | Maximum expected distance |

### 8. Timeline & Milestones

| Milestone | Target Completion | Deliverables |
|-----------|------------------|--------------|
| Project Setup | Day 1 | Directory structure, documentation framework |
| Agent Design | Day 2-3 | Three agents with system prompts, CLI commands |
| Experiment Execution | Day 4 | All test cases run, outputs collected |
| Analysis & Visualization | Day 5 | Results table, graph, initial findings |
| Documentation & Submission | Day 6-7 | Final report, self-evaluation, all artifacts |

### 9. Dependencies & Assumptions

#### 9.1 Technical Dependencies
- LLM API access (OpenAI API or Claude API)
- Python 3.8+ with libraries: `openai`, `numpy`, `scipy`, `matplotlib`, `pandas`
- CLI tools for agent execution
- Embedding model access (OpenAI embeddings or similar)

#### 9.2 Assumptions
- LLM agents will handle spelling errors gracefully
- Translation quality will degrade predictably with error rate increase
- Cosine distance will show positive correlation with error rate
- Agents maintain semantic meaning across language transitions

### 10. Deliverables

**Documentation:**
- ✓ PRD (this document)
- ✓ Architecture documentation (C4 diagrams, system descriptions)
- ✓ Comprehensive README
- ✓ Agent descriptions with system prompts
- ✓ Cost analysis with token breakdowns

**Code & Scripts:**
- ✓ Python embedding calculation script
- ✓ Test data with error injection
- ✓ Results aggregation and visualization scripts
- ✓ Configuration files (.env, config.yaml)

**Analysis & Results:**
- ✓ Experiment results table (6 error rates)
- ✓ Line graph: Error Rate vs. Vector Distance
- ✓ Comprehensive analysis documentation
- ✓ Findings and conclusions summary

**Project Management:**
- ✓ Self-evaluation form (completed)
- ✓ All artifacts version-controlled in Git
- ✓ Professional project structure following best practices

### 11. Success Definition

The project is successful when:
1. ✓ All three agents execute correctly via CLI
2. ✓ All 6 test cases (0-50% errors) complete successfully
3. ✓ Vector distances are calculated and visualized
4. ✓ Clear trend is visible showing error propagation
5. ✓ Full documentation is provided for reproducibility
6. ✓ Analysis provides actionable insights about error resilience
7. ✓ Project meets quality standards from software submission guidelines
