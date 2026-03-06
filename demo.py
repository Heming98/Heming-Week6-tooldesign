"""
Integration Demo: Text Statistics Tool used in an agent/workflow context.

This script demonstrates:
  1. Tool being called by an agent/workflow (simulated by default; real LLM if API key provided)
  2. Successful execution with real text
  3. Error handling with bad input (empty string, wrong type)

To run with a real LLM (e.g. DeepSeek): set environment variable DEEPSEEK_API_KEY
(or LLM_API_KEY) and install the openai package (pip install openai). Then the
first demo will use the LLM as the agent that "decides" to call the tool.
"""
from __future__ import annotations

import os
from typing import Any

from tool import TEXT_STATISTICS_TOOL, text_statistics, Tool


def get_llm_config() -> tuple[str | None, str | None]:
    """
    Read LLM API key and optional base URL from environment.
    Used so the demo can run with a real LLM when the user provides a key.

    Returns:
        (api_key, base_url). Either may be None. base_url is for OpenAI-compatible
        APIs (e.g. DeepSeek: https://api.deepseek.com).
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL") or (
        "https://api.deepseek.com" if os.environ.get("DEEPSEEK_API_KEY") else None
    )
    return (api_key, base_url)


def run_workflow_with_llm(
    task: str, input_data: dict[str, Any], api_key: str, base_url: str | None = None
) -> dict[str, Any]:
    """
    Run the agent workflow using a real LLM: the LLM is prompted to decide whether
    to call the text_statistics tool; we then execute the tool and return the result.
    Requires the 'openai' package (OpenAI-compatible API, e.g. DeepSeek).
    """
    try:
        from openai import OpenAI
    except ImportError:
        return {
            "success": False,
            "error": "LLM mode requires 'openai' package. Install with: pip install openai",
        }

    client = OpenAI(api_key=api_key, base_url=base_url or None)
    tool = TEXT_STATISTICS_TOOL
    text = input_data.get("text", "")

    system_prompt = (
        f"You are an agent with access to this tool: {tool.name}. "
        f"Description: {tool.description} "
        "When the user asks you to analyze text, you should use this tool. "
        "Reply with exactly: USE_TOOL"
    )
    user_prompt = f"User request: {task}\n\nText to analyze: {text!r}"

    try:
        response = client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", "deepseek-chat"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        choice = response.choices[0] if response.choices else None
        if choice and "USE_TOOL" in (choice.message.content or ""):
            return tool.execute(**input_data)
        # If LLM didn't say USE_TOOL, still run the tool for demo (user asked to analyze)
        return tool.execute(**input_data)
    except Exception as e:
        return {"success": False, "error": f"LLM call failed: {e}"}


def run_workflow(
    task: str,
    input_data: dict,
    api_key: str | None = None,
    base_url: str | None = None,
) -> dict:
    """
    Run the agent workflow: either with a real LLM (if api_key is provided and
    openai is installed) or with a simulated agent that always calls the tool.
    """
    agent_name = "TextAnalysisAgent"
    tool = TEXT_STATISTICS_TOOL

    use_llm = False
    if api_key:
        try:
            from openai import OpenAI  # noqa: F401
            use_llm = True
        except ImportError:
            pass

    if use_llm:
        print(f"[Workflow] Agent: {agent_name} (real LLM)")
        print(f"[Workflow] Task: {task}")
        print(f"[Workflow] LLM will decide to call tool: {tool.name}")
        print(f"[Workflow] Executing with params: {input_data}")
        print()
        return run_workflow_with_llm(task, input_data, api_key, base_url)

    # Simulated workflow (no LLM)
    print(f"[Workflow] Agent: {agent_name} (simulated)")
    print(f"[Workflow] Task: {task}")
    print(f"[Workflow] Selected tool: {tool.name}")
    print(f"[Workflow] Executing with params: {input_data}")
    print()
    return tool.execute(**input_data)


def main() -> None:
    api_key, base_url = get_llm_config()
    if api_key:
        try:
            from openai import OpenAI  # noqa: F401
            llm_status = "Real LLM (API key provided)"
        except ImportError:
            llm_status = "Simulated (API key set but 'openai' not installed; pip install openai for LLM)"
    else:
        llm_status = "Simulated (set DEEPSEEK_API_KEY or LLM_API_KEY for real LLM)"

    print("=" * 60)
    print("INTEGRATION DEMO: Text Statistics Tool")
    print("=" * 60)
    print(f"Mode: {llm_status}")
    print()

    # -------------------------------------------------------------------------
    # 1. Successful execution (agent workflow; uses LLM if API key set)
    # -------------------------------------------------------------------------
    print("--- Demo 1: Successful execution (agent workflow) ---")
    sample_text = (
        "The company reported strong earnings this quarter. "
        "Revenue increased by 15 percent. Investors reacted positively."
    )
    task = "Analyze the following news snippet and report text statistics."
    out = run_workflow(task, {"text": sample_text}, api_key=api_key, base_url=base_url)

    if out.get("success") is True:
        print("[Result] Success")
        for key, value in out.get("result", out).items():
            if key != "success":
                print(f"  {key}: {value}")
    else:
        print("[Result] Error:", out.get("error", "Unknown"))
    print()

    # -------------------------------------------------------------------------
    # 2. Error handling: empty string (bad input) — always simulated for predictability
    # -------------------------------------------------------------------------
    print("--- Demo 2: Error handling (empty string) ---")
    out_bad = run_workflow("Analyze this text.", {"text": "   \n\t  "}, api_key=None, base_url=None)
    if out_bad.get("success") is False:
        print("[Result] Caught error as expected:", out_bad.get("error"))
    else:
        print("[Result] Unexpected success:", out_bad)
    print()

    # -------------------------------------------------------------------------
    # 3. Error handling: wrong type (bad input) — always simulated
    # -------------------------------------------------------------------------
    print("--- Demo 3: Error handling (wrong type) ---")
    out_type = run_workflow("Analyze this.", {"text": 12345}, api_key=None, base_url=None)  # type: ignore[arg-type]
    if out_type.get("success") is False:
        print("[Result] Caught error as expected:", out_type.get("error"))
    else:
        print("[Result] Unexpected success:", out_type)
    print()

    # -------------------------------------------------------------------------
    # 4. Edge case: minimal input (single word) — always simulated
    # -------------------------------------------------------------------------
    print("--- Demo 4: Edge case (single word) ---")
    out_edge = run_workflow("Get stats for one word.", {"text": "Hello."}, api_key=None, base_url=None)
    if out_edge.get("success") is True:
        print("[Result] Success (edge case handled)")
        for key, value in out_edge.get("result", out_edge).items():
            if key != "success":
                print(f"  {key}: {value}")
    print()

    # -------------------------------------------------------------------------
    # 5. Direct function call (no wrapper) to show raw output
    # -------------------------------------------------------------------------
    print("--- Demo 5: Direct function call (success) ---")
    direct = text_statistics("Short sentence. Another one.")
    print("[Result]", direct)
    print()

    print("=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
