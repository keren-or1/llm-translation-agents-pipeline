# Cost Analysis - Token Usage and Expense Breakdown

## Overview

This document provides a complete analysis of API token usage and associated costs for running the LLM Translation Agents Pipeline.

## Cost Structure

### OpenAI Pricing (as of November 2024)

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| gpt-4-turbo | $0.01 per 1K tokens | $0.03 per 1K tokens | Primary translation model |
| text-embedding-3-small | $0.02 per 1M tokens | N/A | For vector embeddings |
| gpt-3.5-turbo | $0.0005 per 1K tokens | $0.0015 per 1K tokens | Budget alternative |

### Anthropic Claude Pricing (as of November 2024)

| Model | Input | Output |
|-------|-------|--------|
| Claude 3 Opus | $15 per 1M tokens | $75 per 1M tokens |
| Claude 3 Sonnet | $3 per 1M tokens | $15 per 1M tokens |
| Claude 3 Haiku | $0.25 per 1M tokens | $1.25 per 1M tokens |

## Token Estimation

### Per-Sentence Cost Breakdown

**Experiment Setup:**
- Test sentences: 5 sentences
- Error rates: 6 rates (0%, 10%, 20%, 30%, 40%, 50%)
- Language pairs: 3 (ENG→FRA, FRA→HE, HE→ENG)
- Total agent calls: 5 × 6 × 3 = 90 calls

### Average Token Usage Per Call

| Stage | Model | Input Tokens | Output Tokens | Notes |
|-------|-------|--------------|---------------|-------|
| Agent A (ENG→FRA) | GPT-4-Turbo | ~150-200 | ~120-150 | English to French |
| Agent B (FRA→HE) | GPT-4-Turbo | ~150-200 | ~120-150 | French to Hebrew |
| Agent C (HE→ENG) | GPT-4-Turbo | ~150-200 | ~120-150 | Hebrew to English |
| Embeddings (per pair) | text-embedding-3-small | ~50-100 | N/A | Two texts per pair |

### Translation Phase Cost (Using OpenAI GPT-4)

```
Agent A (90 calls):
  Input:  90 calls × 175 avg tokens × 0.01/1K = $0.16
  Output: 90 calls × 135 avg tokens × 0.03/1K = $0.36
  Subtotal: $0.52

Agent B (90 calls):
  Input:  90 calls × 175 avg tokens × 0.01/1K = $0.16
  Output: 90 calls × 135 avg tokens × 0.03/1K = $0.36
  Subtotal: $0.52

Agent C (90 calls):
  Input:  90 calls × 175 avg tokens × 0.01/1K = $0.16
  Output: 90 calls × 135 avg tokens × 0.03/1K = $0.36
  Subtotal: $0.52

Translation Phase Total: $1.56
```

### Embeddings Phase Cost

```
Embeddings Calculation:
  Pairs to embed: 6 error rates × 2 texts/pair = 12 texts
  Tokens per text: ~75 average
  Total tokens: 12 × 75 = 900 tokens
  Cost: 900 × 0.02/1M = $0.000018 (negligible)

Embeddings Phase Total: ~$0.00
```

### Estimated Total Cost

| Component | Estimated Cost |
|-----------|-----------------|
| Translation (all agents) | $1.56 |
| Embeddings | ~$0.00 |
| **Total (GPT-4)** | **~$1.56** |

*Note: Actual costs may vary ±10-20% based on sentence length and complexity*

## Budget Alternatives

### Using GPT-3.5-Turbo (Budget Option)

```
GPT-3.5-Turbo Cost:
  Input:  270 calls × 175 tokens × 0.0005/1K = $0.024
  Output: 270 calls × 135 tokens × 0.0015/1K = $0.055
  Total: ~$0.08
```

**Savings:** ~95% reduction in cost
**Trade-off:** Lower translation quality, more errors

### Using Claude 3 Sonnet

```
Claude 3 Sonnet Cost:
  Input:  270 calls × 175 tokens × 0.003/1M = $0.142
  Output: 270 calls × 135 tokens × 0.015/1M = $0.547
  Total: ~$0.69
```

**Comparison:** ~44% cheaper than GPT-4, comparable quality

## Cost Optimization Strategies

### 1. Batch Processing
- Batch multiple texts in a single API call
- **Potential savings:** 10-15%
- **Trade-off:** Slightly longer processing time

### 2. Smaller Sentences
- Use shorter test sentences (15-20 words instead of 25+)
- **Potential savings:** 5-10%
- **Trade-off:** Less nuanced error propagation

### 3. Fewer Error Rates
- Test fewer error percentages (e.g., 0%, 25%, 50%)
- **Potential savings:** 33-50%
- **Trade-off:** Less detailed analysis

### 4. Caching Responses
- Cache identical prompts (enable if rerunning)
- **Potential savings:** 10-20% (if reruns)
- **Trade-off:** Requires storage

### 5. Lower Temperature/More Consistent Outputs
- Reduce retries due to consistency
- **Potential savings:** 5%
- **Trade-off:** Minimal

## Cost Tracking in Experiment

### Token Usage Log

The system tracks token usage in `results/analysis/tokens_log.json`:

```json
{
  "experiment": {
    "total_calls": 90,
    "date": "2024-11-14",
    "duration_seconds": 3600
  },
  "agents": {
    "agent_a": {
      "calls": 30,
      "input_tokens": 5250,
      "output_tokens": 4050
    },
    "agent_b": {
      "calls": 30,
      "input_tokens": 5250,
      "output_tokens": 4050
    },
    "agent_c": {
      "calls": 30,
      "input_tokens": 5250,
      "output_tokens": 4050
    }
  },
  "embeddings": {
    "texts_embedded": 12,
    "tokens_used": 900
  },
  "totals": {
    "total_input_tokens": 15750,
    "total_output_tokens": 12150,
    "total_tokens": 27900,
    "estimated_cost_usd": 1.56
  }
}
```

## Cost Report Generation

To generate a cost report after running experiments:

```bash
python src/cost_analyzer.py \
  --tokens-log results/analysis/tokens_log.json \
  --output results/analysis/cost_report.md \
  --model gpt-4-turbo
```

Output includes:
- Detailed breakdown by agent
- Cost per error rate
- Cost per sentence
- Model comparison analysis

## Scaling Considerations

### For Larger Experiments

| Scenario | Cost | Time |
|----------|------|------|
| 1 sentence, 6 error rates | ~$0.26 | ~5-10 minutes |
| 5 sentences, 6 error rates | ~$1.30 | ~25-50 minutes |
| 10 sentences, 6 error rates | ~$2.60 | ~50-100 minutes |
| 20 sentences, 6 error rates | ~$5.20 | ~2-4 hours |

### Long-Running Experiments

For extended research:
- Consider using Claude 3 Sonnet for 44% cost savings
- Use batch processing to optimize API calls
- Cache intermediate results
- Run during off-peak hours (potential discounts with some providers)

## Budget Planning

### Free Tier Limits

**OpenAI Free Trial:**
- $5 free credits (valid 3 months)
- Enough for ~3 full experiments

**Claude Free Tier:**
- Limited rate limiting, no cost
- Slower responses
- Good for testing/development

### Recommended Budget

**For This Assignment:**
- **Minimum:** $2 (use GPT-3.5-turbo)
- **Recommended:** $5-10 (use GPT-4 with reasonable parameters)
- **Optimal:** $10-20 (GPT-4 with multiple experiments/variations)

## Cost-Benefit Analysis

### Value vs. Cost

| Metric | Benefit |
|--------|---------|
| Reproducibility | High - Full cost transparency |
| Scalability | Excellent - Linear cost increase |
| Quality | High - Research-grade results |
| Cost Efficiency | Good - ~$1-2 for complete analysis |

### ROI for Academic Context

- **Cost:** ~$2-5 per complete experiment
- **Time Saved:** Hours of manual analysis
- **Quality Gained:** Quantitative metrics, visualizations
- **Learning Value:** Understanding LLM error propagation
- **Overall Value:** Exceptional for academic research

## Environmental Impact

### API Energy Consumption

Estimated CO2 emissions per 1M tokens:
- OpenAI's infrastructure: ~0.5-1g CO2
- Anthropic's infrastructure: ~0.5-1g CO2

**Total experiment footprint:** ~0.01-0.05g CO2 (equivalent to ~0.001 miles of driving)

## References

- OpenAI Pricing: https://openai.com/pricing
- Anthropic Pricing: https://www.anthropic.com/pricing
- Environmental Impact: https://openai.com/research/carbon-emissions

---

**Last Updated:** November 14, 2024
**Version:** 1.0
