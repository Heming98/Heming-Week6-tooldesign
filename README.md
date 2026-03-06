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

**Prerequisites:** Python 3.8+ (no external packages required for simulated mode; standard library only).

From the assignment directory, run:

```bash
python demo.py
```

**Running with a real LLM (e.g. DeepSeek):** The code is structured so it can run with a real LLM if you provide an API key. (1) Set one of: `DEEPSEEK_API_KEY` or `LLM_API_KEY` (environment variable). (2) Optionally set `LLM_BASE_URL` (default for DeepSeek is `https://api.deepseek.com`) and `LLM_MODEL` (default `deepseek-chat`). (3) Install the OpenAI-compatible client: `pip install openai`. Then run `python demo.py` as above. Demo 1 will use the LLM as the agent that decides to call the tool; demos 2–5 stay simulated so error handling and edge cases remain predictable. Instructions are not redundant: without them, a recipient of `tool.py`/`demo.py` would not know where to set the key or that the optional dependency is needed.

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

## Tool design for an AI agent — appropriateness and readability

**Is the current tool design appropriate for an AI agent?** Yes. The tool has a single, clear task (analyze text and return statistics), a well-defined input (one string) and output (a JSON-serializable dict). That makes it easy for an agent (or LLM) to choose when to call it and how to use the result. The `Tool` wrapper exposes a **name** and **description** so the agent can decide “I need text statistics” and **execute(**kwargs)** so the workflow can run it without knowing implementation details.

**Would we measure readability with an LLM instead of a formula?** It depends on the goal. A **formula** (like the one we use) is deterministic, fast, free, and works offline—good for assignments and for tools that must behave the same every time. An **LLM** could judge “how easy this is to read” in a more human-like way (e.g. tone, jargon, structure), but it would cost API calls, be slower, and vary between runs. For a **course assignment**, the formula is a better fit: it shows you can design a tool with clear inputs/outputs and error handling without adding API cost or nondeterminism. In a production system, you might offer both: a fast formula-based score plus an optional “LLM readability” tool for deeper analysis.

## Where the LLM API key is used (and how someone else can use the tool)

**Role of the API key in our code:** The **tool itself** (`tool.py`) does **not** use any API key. It only does local text analysis. The API key is used only in **demo.py**, in the **agent workflow**: when you set `DEEPSEEK_API_KEY` (or `LLM_API_KEY`), the demo uses that key to call a real LLM (e.g. DeepSeek) so the **agent** is the LLM—it “decides” to call the tool, and our code then runs `TEXT_STATISTICS_TOOL.execute(**input_data)`. So: **tool = no key; demo’s agent = key optional.**

**If someone else receives only `tool.py`:** They can call `text_statistics(text)` or `TEXT_STATISTICS_TOOL.execute(text=...)` directly in their own script or agent framework; no API key is required. **If they also have `demo.py`** and want the demo to use a real LLM, they need to know where to put the key (environment variables above) and that `openai` is optional for that. So **instructions are not redundant**—they should be told to set `DEEPSEEK_API_KEY` or `LLM_API_KEY` and optionally install `openai` if they want the demo to run with a real LLM.

## Deliverables

- `tool.py` — Tool wrapper class and `text_statistics` implementation
- `demo.py` — Integration demo (workflow + success + error cases)
- `README.md` — this file
- `prompt-log.md` — full AI chat history