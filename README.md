# Mini-Assignment 2: Tool Design — Text Statistics & Readability

## What the tool does

The **Text Statistics & Readability** tool analyzes a string of text and returns:

- **word_count** — number of words (whitespace-separated)
- **sentence_count** — number of sentences (split on `.` `!` `?`)
- **character_count** — length of trimmed text
- **avg_word_length** — average characters per word
- **avg_sentence_length** — average words per sentence
- **readability_score** — a heuristic score from 0 to 100 (higher = easier to read)

It is intended for **business/news/text analysis** (e.g., quality checks, content briefs, or pre-processing for summarization). The tool is implemented as a reusable function plus a small `Tool` wrapper so it can be registered with an agent or workflow.

**Realistic use case:** A communications team uses this tool inside an agent workflow to check every press release before publishing: the agent receives the draft, calls the text-statistics tool, and flags pieces whose readability score is below a threshold (e.g. 60) for simplification.

## How to run the demo

**Prerequisites:** Python 3.8+ (no external packages required; only the standard library is used).

From the assignment directory, run:

```bash
python demo.py
```

You should see:

1. **Successful execution** — a simulated agent workflow calls the tool on a sample news snippet and prints the statistics.
2. **Error handling (empty string)** — the workflow passes whitespace-only input and the tool returns a structured error.
3. **Error handling (wrong type)** — the workflow passes a non-string (e.g. integer) and the tool returns a structured error.
4. **Edge case (single word)** — the tool correctly handles minimal input (one word, one sentence).
5. **Direct function call** — the underlying `text_statistics()` function is called directly to show raw output.

## Design decisions and limitations

- **Tool wrapper:** The `Tool` class holds a name, description, and function. `execute(**kwargs)` runs the function and catches exceptions, returning a JSON-serializable dict with `success: true/false` and either `result` or `error`. This keeps agent-facing responses consistent and avoids uncaught exceptions.
- **Input validation:** The text must be a non-empty string (after stripping). Non-strings raise `TypeError`; empty/whitespace raises `ValueError`. These are caught in `Tool.execute()` and turned into structured error responses.
- **Readability formula:** A simple heuristic is used: score = 100 − (2 × avg_word_length + 0.5 × avg_sentence_length), clamped to 0–100. No external libraries or ML models; suitable for quick comparisons, not for standardized readability grades (e.g. Flesch–Kincaid would require a proper formula or library).
- **Limitations:** Sentence splitting is punctuation-based and may mis-count in edge cases (e.g. abbreviations, decimals). The readability score is not calibrated to a specific standard. The tool is English-oriented (word/sentence boundaries).

## Deliverables

- `tool.py` — Tool wrapper class and `text_statistics` implementation
- `demo.py` — Integration demo (workflow + success + error cases)
- `README.md` — this file
- `prompt-log.md` — full AI chat history