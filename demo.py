"""
Integration Demo: Text Statistics Tool used in an agent/workflow context.

This script demonstrates:
  1. Tool being called by a simulated agent/workflow
  2. Successful execution with real text
  3. Error handling with bad input (empty string, wrong type)
"""

from tool import TEXT_STATISTICS_TOOL, text_statistics, Tool


def run_workflow(task: str, input_data: dict) -> dict:
    """
    Simulated workflow: an "agent" receives a task and selects then executes a tool.

    In a full CrewAI/LLM setup, the agent would choose the tool by name and pass
    parameters; here we simulate that by mapping the task to our text_statistics tool.
    """
    agent_name = "TextAnalysisAgent"
    tool = TEXT_STATISTICS_TOOL

    print(f"[Workflow] Agent: {agent_name}")
    print(f"[Workflow] Task: {task}")
    print(f"[Workflow] Selected tool: {tool.name}")
    print(f"[Workflow] Executing with params: {input_data}")
    print()

    result = tool.execute(**input_data)
    return result


def main() -> None:
    print("=" * 60)
    print("INTEGRATION DEMO: Text Statistics Tool")
    print("=" * 60)
    print()

    # -------------------------------------------------------------------------
    # 1. Successful execution (tool used in context)
    # -------------------------------------------------------------------------
    print("--- Demo 1: Successful execution (agent workflow) ---")
    sample_text = (
        "The company reported strong earnings this quarter. "
        "Revenue increased by 15 percent. Investors reacted positively."
    )
    task = "Analyze the following news snippet and report text statistics."
    out = run_workflow(task, {"text": sample_text})

    if out.get("success") is True:
        print("[Result] Success")
        for key, value in out.get("result", out).items():
            if key != "success":
                print(f"  {key}: {value}")
    else:
        print("[Result] Error:", out.get("error", "Unknown"))
    print()

    # -------------------------------------------------------------------------
    # 2. Error handling: empty string (bad input)
    # -------------------------------------------------------------------------
    print("--- Demo 2: Error handling (empty string) ---")
    out_bad = run_workflow("Analyze this text.", {"text": "   \n\t  "})
    if out_bad.get("success") is False:
        print("[Result] Caught error as expected:", out_bad.get("error"))
    else:
        print("[Result] Unexpected success:", out_bad)
    print()

    # -------------------------------------------------------------------------
    # 3. Error handling: wrong type (bad input)
    # -------------------------------------------------------------------------
    print("--- Demo 3: Error handling (wrong type) ---")
    out_type = run_workflow("Analyze this.", {"text": 12345})  # type: ignore[arg-type]
    if out_type.get("success") is False:
        print("[Result] Caught error as expected:", out_type.get("error"))
    else:
        print("[Result] Unexpected success:", out_type)
    print()

    # -------------------------------------------------------------------------
    # 4. Edge case: minimal input (single word, single sentence)
    # -------------------------------------------------------------------------
    print("--- Demo 4: Edge case (single word) ---")
    out_edge = run_workflow("Get stats for one word.", {"text": "Hello."})
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
