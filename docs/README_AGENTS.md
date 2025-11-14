# LLM Agents Detailed Specifications

This document provides complete specifications for the three LLM agents in the translation pipeline.

## Overview

The system employs three LLM agents in a sequential chain:
- **Agent A:** English → French translator
- **Agent B:** French → Hebrew translator
- **Agent C:** Hebrew → English back-translator

Each agent has a specialized system prompt and is configured with specific parameters for optimal performance.

---

## Agent A: English → French Translator

### Purpose
Translate English text (potentially containing spelling errors) to French while maintaining semantic meaning.

### Design Rationale
Agent A is positioned at the entry point of the translation chain. Its primary challenge is handling spelling errors gracefully while maintaining accuracy. This agent sets the tone for the entire pipeline—if it captures meaning despite input errors, subsequent agents have a better foundation.

### Agent Skills

The following core **skills** are explicitly required and embedded in Agent A's system prompt:

| Skill | Definition | Implementation | Verification |
|-------|-----------|-----------------|--------------|
| **Translation Accuracy** | Render source text meaning into target language correctly | Use professional vocabulary, maintain grammatical structure, preserve semantic nuance | Compare similarity scores across error rates |
| **Error Robustness** | Handle misspelled/corrupted input by inferring intent | Contextual analysis of malformed words, fallback to phonetic similarity | Works with 0-50% spelling errors without failure |
| **Meaning Preservation** | Maintain original intent, tone, and information across languages | Literal accuracy + idiomatic expression, no omissions | Cosine distance correlates linearly with input error rate |
| **Semantic Coherence** | Produce output that flows naturally and makes sense as a whole | Proper grammar, natural phrasing, logical sentence structure | Output is fluent and grammatically correct French |

### System Prompt (With Explicit Skills)

```
You are a professional English-to-French translator with extensive experience in multilingual communication and error-resilient translation.

ROLE: Your primary task is to translate English text into French, even when the input contains spelling errors or unusual phrasings.

CORE INSTRUCTIONS:
1. Translate accurately while preserving the original meaning, tone, and nuance
2. When encountering misspelled words:
   - Infer the intended word from context
   - Maintain semantic consistency
   - Never explicitly comment on the errors
3. Use natural, idiomatic French phrasing (contemporary standard French)
4. Preserve proper nouns, numbers, and technical terms appropriately
5. If you encounter ambiguous text, provide your best interpretation based on context
6. Maintain grammatical accuracy and proper French conventions

OUTPUT REQUIREMENTS:
- Provide ONLY the French translation
- Do not include explanations, notes, or meta-commentary
- Do not translate proper nouns unless contextually appropriate
- Maintain sentence structure fidelity when possible

QUALITY STANDARDS:
- Accuracy: Semantic meaning preserved
- Fluency: Natural French, not literal translation
- Completeness: All elements translated
- Consistency: Technical terms used consistently throughout
```

### Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | gpt-4-turbo (or claude-3-opus) | High translation quality, handles nuance well |
| Temperature | 0.3 | Low temp = more consistent, less creative interpretation |
| Max Tokens | 2000 | Sufficient for ~500-word sentences |
| Top P | 0.9 | Balanced diversity and consistency |
| Stop Sequences | None | Let model naturally complete translation |

### Input Specification

**Format:** Plain text sentence(s)

**Requirements:**
- Minimum 15 words
- May contain 0-50% spelling errors
- Single or multiple sentences acceptable
- Any topic domain acceptable

**Example Input (with errors):**
```
The quikc brown fox jumps over the lazy dog in the sunny afternoon with greet enthusiasm.
```

### Expected Output Format

**Format:** Plain text in French

**Characteristics:**
- Single or multiple sentences matching input count
- Natural French phrasing
- No explanatory text
- Handles errors transparently

**Example Output:**
```
Le rapide renard brun saute par-dessus le chien paresseux dans l'après-midi ensoleillé avec grand enthousiasme.
```

### Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Input Handling | Processes any text without errors |
| Error Robustness | Semantic meaning preserved despite spelling errors |
| Output Quality | Fluent French, grammatically correct |
| Consistency | Terminology consistent throughout |
| Performance | Completes in <60 seconds |

---

## Agent B: French → Hebrew Translator

### Purpose
Translate French text (from Agent A output) to Hebrew, maintaining semantic continuity from the original English.

### Design Rationale
Agent B operates as the middle translator, receiving output from Agent A. At this stage, some information degradation may have occurred. Agent B must preserve whatever meaning remains while producing grammatically correct Hebrew. This is a challenging transition between two very different language families (Romance to Semitic).

### System Prompt

```
You are a professional French-to-Hebrew translator with deep expertise in both Romance and Semitic language structures.

ROLE: Your task is to translate French text into Hebrew, preserving meaning and structure from the source.

CORE INSTRUCTIONS:
1. Translate with high semantic fidelity to the French source text
2. Use standard Modern Hebrew (תרגום לעברית תקנית עדכנית)
3. Preserve meaning even if the French text has unusual phrasing or potential errors from earlier translation
4. Maintain proper noun capitalization and transliteration conventions
5. Structure Hebrew sentences naturally while respecting source meaning
6. Handle technical terms and domain-specific vocabulary appropriately
7. If uncertain about French meaning, preserve structure and provide best interpretation

OUTPUT REQUIREMENTS:
- Provide ONLY the Hebrew translation
- Use standard Hebrew characters (Unicode Hebrew block)
- Do not include explanations, back-translations, or meta-commentary
- Maintain proper formatting and punctuation

QUALITY STANDARDS:
- Semantic Fidelity: Meaning from French source preserved
- Grammatical Correctness: Proper Modern Hebrew grammar and syntax
- Idiomaticity: Natural Hebrew phrasing where possible
- Clarity: Reader can understand intended meaning
```

### Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | gpt-4-turbo (or claude-3-opus) | Handles non-Latin scripts well, good translation quality |
| Temperature | 0.3 | Consistency over creativity |
| Max Tokens | 2000 | Sufficient for Hebrew output |
| Top P | 0.9 | Balanced sampling |
| Stop Sequences | None | Natural completion |

### Input Specification

**Format:** Plain text in French (output from Agent A)

**Characteristics:**
- Theoretically correct French from Agent A
- May reflect translation artifacts from English source
- May contain degraded semantic content due to error propagation
- One or more sentences

**Example Input (from Agent A):**
```
Le rapide renard brun saute par-dessus le chien paresseux dans l'après-midi ensoleillé avec grand enthousiasme.
```

### Expected Output Format

**Format:** Plain text in Hebrew

**Characteristics:**
- Natural Modern Hebrew
- Preserves source structure when appropriate
- No explanatory text
- May reflect semantic degradation from original English

**Example Output:**
```
השועל החום המהיר קופץ מעל הכלב העצלן בצהריים בחזון גדול בחום התשוקה.
```

### Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Hebrew Correctness | Valid Modern Hebrew, proper grammar |
| Semantic Preservation | Meaning from French source maintained |
| Character Encoding | Proper Hebrew Unicode encoding |
| Output Completeness | All source material translated |
| Performance | Completes in <60 seconds |

---

## Agent C: Hebrew → English Back-Translator

### Purpose
Translate Hebrew output (from Agent B) back to English for final comparison with original input.

### Design Rationale
Agent C completes the cycle by back-translating to English. This is the critical comparison point—comparing Agent C's output with the original input reveals accumulated error propagation through the entire chain. Agent C must produce natural English while constrained by the degraded Hebrew input.

### System Prompt

```
You are a professional Hebrew-to-English translator with expertise in producing natural, fluent English translations.

ROLE: Your task is to translate Hebrew text into English, producing natural, idiomatic English output.

CORE INSTRUCTIONS:
1. Translate to natural, contemporary English
2. Preserve the semantic content of the Hebrew source as much as possible
3. Use proper English grammar and spelling
4. Structure English sentences naturally (not literal translation)
5. Maintain proper nouns and technical terms appropriately
6. If the Hebrew text seems unclear or contains unusual phrasing, provide your best interpretation
7. Prioritize fluency and readability for English readers

OUTPUT REQUIREMENTS:
- Provide ONLY the English translation
- Use standard English spelling and grammar
- Do not include explanations, back-translations, or notes
- No meta-commentary about translation challenges
- Maintain punctuation and formatting

QUALITY STANDARDS:
- Semantic Fidelity: Meaning from Hebrew preserved as much as possible
- English Quality: Natural, fluent, properly spelled English
- Readability: Clear to native English speakers
- Completeness: All source material translated
- Authenticity: Sounds like natural English, not translation
```

### Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | gpt-4-turbo (or claude-3-opus) | Strong English generation, good back-translation |
| Temperature | 0.3 | Consistency, avoiding creative deviations |
| Max Tokens | 2000 | Sufficient for English translation of Hebrew text |
| Top P | 0.9 | Balanced sampling |
| Stop Sequences | None | Natural completion |

### Input Specification

**Format:** Plain text in Hebrew (output from Agent B)

**Characteristics:**
- Modern Hebrew from Agent B
- May contain meaning degradation from original English due to error propagation
- One or more sentences
- Potentially unusual phrasings reflecting source errors

**Example Input (from Agent B):**
```
השועל החום המהיר קופץ מעל הכלב העצלן בצהריים בחזון גדול בחום התשוקה.
```

### Expected Output Format

**Format:** Plain text in English

**Characteristics:**
- Natural English phrasing
- May differ semantically from original input
- No explanatory content
- Reflects accumulated error from chain

**Example Output:**
```
The fast brown fox jumps over the lazy dog in the afternoon with great passion and enthusiasm.
```

### Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| English Quality | Natural, idiomatic English |
| Semantic Relationship | Relationship to original measurable by cosine distance |
| Completeness | All Hebrew translated |
| Clarity | Clear meaning to English reader |
| Performance | Completes in <60 seconds |

---

## Comparative Agent Specifications

### Language Pair Difficulty

| Agent | From | To | Difficulty | Notes |
|-------|------|-----|-----------|-------|
| A | English | French | Medium | Both Indo-European, similar grammar structures |
| B | French | Hebrew | Hard | Romance to Semitic, very different structures |
| C | Hebrew | English | Medium | Back-translation, Semitic to Indo-European |

### Cumulative Error Impact

**Error Propagation Expected:**
- Agent A: Input errors handled, output clean French
- Agent B: Semantic loss possible due to language family differences
- Agent C: Highest loss due to double translation + degraded input

**Cosine Distance Prediction:**
- 0% errors: ~0.05 (minimal distance)
- 10% errors: ~0.10-0.15 (slight degradation)
- 20% errors: ~0.20-0.30 (moderate degradation)
- 30% errors: ~0.35-0.45 (significant degradation)
- 40% errors: ~0.50-0.60 (major degradation)
- 50% errors: ~0.65-0.75 (extreme degradation)

---

## Configuration Examples

### config/agent_prompts.yaml

```yaml
agents:
  agent_a:
    name: "English to French Translator"
    language_pair: "en_to_fr"
    model: "gpt-4-turbo"
    temperature: 0.3
    top_p: 0.9
    max_tokens: 2000
    system_prompt: |
      You are a professional English-to-French translator...
      [Full prompt as shown above]

  agent_b:
    name: "French to Hebrew Translator"
    language_pair: "fr_to_he"
    model: "gpt-4-turbo"
    temperature: 0.3
    top_p: 0.9
    max_tokens: 2000
    system_prompt: |
      You are a professional French-to-Hebrew translator...
      [Full prompt as shown above]

  agent_c:
    name: "Hebrew to English Back-Translator"
    language_pair: "he_to_en"
    model: "gpt-4-turbo"
    temperature: 0.3
    top_p: 0.9
    max_tokens: 2000
    system_prompt: |
      You are a professional Hebrew-to-English translator...
      [Full prompt as shown above]

embeddings:
  model: "text-embedding-3-small"
  dimensions: 1536
  batch_size: 32
```

---

## Execution Workflow

### CLI Command Templates

**Agent A - English to French:**
```bash
curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-turbo",
    "temperature": 0.3,
    "max_tokens": 2000,
    "messages": [
      {
        "role": "system",
        "content": "You are a professional English-to-French translator..."
      },
      {
        "role": "user",
        "content": "Translate to French: '"$INPUT_TEXT"'"
      }
    ]
  }' | jq -r '.choices[0].message.content'
```

**Agent B - French to Hebrew:**
```bash
curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-turbo",
    "temperature": 0.3,
    "max_tokens": 2000,
    "messages": [
      {
        "role": "system",
        "content": "You are a professional French-to-Hebrew translator..."
      },
      {
        "role": "user",
        "content": "Translate to Hebrew: '"$AGENT_A_OUTPUT"'"
      }
    ]
  }' | jq -r '.choices[0].message.content'
```

**Agent C - Hebrew to English:**
```bash
curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-turbo",
    "temperature": 0.3,
    "max_tokens": 2000,
    "messages": [
      {
        "role": "system",
        "content": "You are a professional Hebrew-to-English translator..."
      },
      {
        "role": "user",
        "content": "Translate to English: '"$AGENT_B_OUTPUT"'"
      }
    ]
  }' | jq -r '.choices[0].message.content'
```

---

## Testing & Validation

### Manual Testing

Test each agent with a sample sentence:

```bash
# Original test sentence
ORIGINAL="The quick brown fox jumps over the lazy dog in the afternoon."

# Agent A
echo "Testing Agent A (ENG→FRA)..."
AGENT_A_OUTPUT=$(curl ... # as shown above)
echo "$AGENT_A_OUTPUT"

# Agent B
echo "Testing Agent B (FRA→HE)..."
AGENT_B_OUTPUT=$(curl ... # as shown above)
echo "$AGENT_B_OUTPUT"

# Agent C
echo "Testing Agent C (HE→ENG)..."
AGENT_C_OUTPUT=$(curl ... # as shown above)
echo "$AGENT_C_OUTPUT"

# Compare
echo "Original: $ORIGINAL"
echo "Final: $AGENT_C_OUTPUT"
```

### Expected Variations

Different models may produce variations:
- GPT-4: Professional, accurate translations
- Claude 3 Opus: Similar quality, slightly different phrasing
- Claude 3 Sonnet: Good quality, potentially faster

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent refuses to translate | Too strict system prompt | Add "provide best effort translation" clause |
| Output includes explanations | Prompt not strict enough | Add "ONLY output translation, no commentary" |
| Hebrew encoding errors | Character set issues | Ensure UTF-8 encoding, use proper Hebrew Unicode |
| Long execution time | Rate limiting | Add delay between requests, batch processing |
| Inconsistent results | Temperature too high | Reduce temperature to 0.2-0.3 |

---

## Appendix: System Prompt Evolution

The system prompts can be fine-tuned based on results:

**Iteration 1 (Current):** Focus on meaning preservation and error handling

**Iteration 2 (Optional):** Add emphasis on maintaining specific terminology

**Iteration 3 (Optional):** Add constraints on sentence length or structure

Modify `config/agent_prompts.yaml` to test variations.
