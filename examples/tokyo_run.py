"""
examples/tokyo_run.py
Minimal GitHub demo: run the Tokyo Weather AI Agent and print every ReAct step.

Usage (from repo root):
    python examples/tokyo_run.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root OR from examples/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import SimpleAgent

QUERY = "Check the current weather in Tokyo and convert the temperature to Fahrenheit."


def main() -> None:
    print("=" * 60)
    print("TOKYO WEATHER AI AGENT — Live ReAct Run")
    print("=" * 60)
    print(f"GOAL: {QUERY}\n")

    agent = SimpleAgent(mode="simulated")

    for step in agent.run_step_by_step(QUERY):
        print(f"[{step.step_type}] {step.title}")
        print(step.content)
        if step.tool_name:
            print(f"  tool = {step.tool_name}")
            print(f"  args = {step.tool_args}")
        if step.explanation:
            print(f"  description: {step.explanation}")
        print("-" * 60)

    print("\nDone. See YOUTUBE.md for the YouTube description & story.")


if __name__ == "__main__":
    main()
