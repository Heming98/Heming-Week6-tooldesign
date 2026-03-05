"""
Mini-Assignment 2: Custom Tool for AI Agents
Tool: Text Statistics & Readability Analyzer

This module provides a reusable Tool wrapper and a text analysis function
suitable for business/news/text analysis workflows.
"""

from __future__ import annotations

import re
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Tool wrapper class
# ---------------------------------------------------------------------------

class Tool:
    """
    A simple wrapper for an agent-callable tool with a name, description, and function.

    Attributes:
        name: Short identifier for the tool.
        description: Human-readable description for agent/LLM tool selection.
        fn: The callable to execute (should accept keyword arguments).
    """

    def __init__(self, name: str, description: str, fn: Callable[..., Any]) -> None:
        self.name = name
        self.description = description
        self.fn = fn

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        Execute the wrapped function with the given keyword arguments.

        Catches exceptions from the underlying function and returns a structured
        error response instead of raising, so agents can handle failures gracefully.

        Returns:
            A JSON-serializable dict. On success, returns the result of self.fn(**kwargs).
            On failure, returns {"success": False, "error": "<message>"}.
        """
        try:
            result = self.fn(**kwargs)
            if isinstance(result, dict) and "success" not in result:
                return {"success": True, "result": result}
            return result
        except (ValueError, TypeError) as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {e}"}


# ---------------------------------------------------------------------------
# Text Statistics & Readability function
# ---------------------------------------------------------------------------

def text_statistics(text: str) -> dict[str, Any]:
    """
    Compute text statistics and a simple readability score for a given string.

    Useful for business reports, news articles, or any text analysis pipeline
    (e.g., quality checks, summarization pre-processing).

    Parameter schema:
        Inputs:
            text (str): The input text to analyze. Must be a non-empty string.
        Outputs (dict):
            word_count (int): Number of words (whitespace-separated tokens).
            sentence_count (int): Number of sentences (split by . ! ?).
            avg_word_length (float): Average character count per word.
            avg_sentence_length (float): Average word count per sentence.
            readability_score (float): Simple heuristic score 0–100 (higher = easier to read).
            character_count (int): Total character count (excluding leading/trailing spaces).

    Raises:
        TypeError: If `text` is not a string.
        ValueError: If `text` is empty or only whitespace.

    Returns:
        A JSON-serializable dict with the statistics above.
    """
    # Input validation
    if not isinstance(text, str):
        raise TypeError("Input must be a string, got " + type(text).__name__)

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Input text cannot be empty or only whitespace")

    # Character count (excluding leading/trailing spaces)
    character_count = len(cleaned)

    # Word count: split on whitespace, drop empty tokens
    words = [w for w in re.split(r"\s+", cleaned) if w]
    word_count = len(words)

    # Sentence count: split on sentence-ending punctuation
    sentences = [s.strip() for s in re.split(r"[.!?]+", cleaned) if s.strip()]
    sentence_count = max(len(sentences), 1)  # avoid division by zero

    # Averages
    avg_word_length = sum(len(w) for w in words) / word_count if word_count else 0.0
    avg_sentence_length = word_count / sentence_count

    # Simple readability heuristic (higher = easier to read):
    # Penalize long words and long sentences; scale to roughly 0–100.
    # Formula: 100 - (avg_word_length * 2 + avg_sentence_length * 0.5), clamped.
    raw_score = 100.0 - (avg_word_length * 2.0 + avg_sentence_length * 0.5)
    readability_score = max(0.0, min(100.0, round(raw_score, 2)))

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "character_count": character_count,
        "avg_word_length": round(avg_word_length, 2),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "readability_score": readability_score,
    }


# ---------------------------------------------------------------------------
# Pre-configured tool instance for agents
# ---------------------------------------------------------------------------

TEXT_STATISTICS_TOOL = Tool(
    name="text_statistics",
    description=(
        "Analyzes a text string and returns word count, sentence count, "
        "average word length, average sentence length, and a simple readability score (0-100). "
        "Use for business or news text analysis."
    ),
    fn=text_statistics,
)
