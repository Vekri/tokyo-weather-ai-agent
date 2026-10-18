"""
cli_demo.py - Interactive Terminal Demonstration for Video Recording.

Ideal for video tutorials:
- Beautiful Rich UI with colored panels and step counters
- Two presentation modes:
    1. Interactive Mode: Press [Enter] after each step (you control the timing as you talk)
    2. Auto-Play Mode: Pauses automatically between steps for hands-free video recording
"""

import sys
import time
import argparse
from typing import Optional

# Ensure UTF-8 output on Windows PowerShell / CMD
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.markup import escape

from agent import SimpleAgent, AgentStep

console = Console()

PRESET_SCENARIOS = {
    "1": {
        "title": "Smart Financial Analyst (VIP Discount + 8% Sales Tax)",
        "query": "Calculate the total for an order of 50 units at $30 each, apply the VIP discount, and add 8% sales tax."
    },
    "2": {
        "title": "Travel Assistant (Tokyo Weather + Celsius to Fahrenheit)",
        "query": "Check the current weather in Tokyo and convert the temperature to Fahrenheit."
    },
    "3": {
        "title": "Customer Support (Return Policy + Restocking Fee calculation)",
        "query": "A customer wants to return a $200 item purchased 45 days ago. Check the policy and calculate the refund."
    }
}

def print_banner():
    console.print()
    banner_text = (
        "[bold cyan]🤖 AI AGENT STEP-BY-STEP DEMONSTRATION[/bold cyan]\n"
        "[italic white]Understanding the ReAct Loop (Reasoning + Action + Observation)[/italic white]"
    )
    console.print(Panel(banner_text, border_style="bold blue", expand=False))
    console.print()

def render_step(step: AgentStep, total_estimated: int = 7):
    """Render each step in a distinct, visually appealing Rich Panel."""
    step_type = step.step_type
    safe_title = escape(step.title)

    if step_type == "GOAL":
        content = (
            f"[bold yellow]USER GOAL:[/bold yellow] {escape(step.content)}\n\n"
            f"[italic dim]{escape(step.explanation or '')}[/italic dim]"
        )
        console.print(Panel(content, title=f"[bold yellow]{safe_title}[/bold yellow]", border_style="yellow", expand=True))

    elif step_type == "THOUGHT":
        content = (
            f"[bold cyan]Internal Monologue / Reasoning:[/bold cyan]\n"
            f"{escape(step.content)}\n\n"
            f"[italic dim]Why this matters: {escape(step.explanation or '')}[/italic dim]"
        )
        console.print(Panel(content, title=f"[bold cyan]{safe_title}[/bold cyan]", border_style="cyan", expand=True))

    elif step_type == "ACTION":
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Parameter", style="dim")
        table.add_column("Value")
        if step.tool_args:
            for k, v in step.tool_args.items():
                table.add_row(str(k), str(v))
        else:
            table.add_row("Details", step.content)

        console.print(Panel(table, title=f"[bold magenta]{safe_title}[/bold magenta]", border_style="magenta", expand=True))

    elif step_type == "OBSERVATION":
        content = (
            f"[bold green]Tool Execution Result:[/bold green]\n"
            f"[white]{escape(step.content)}[/white]\n\n"
            f"[italic dim]Flow: {escape(step.explanation or '')}[/italic dim]"
        )
        console.print(Panel(content, title=f"[bold green]{safe_title}[/bold green]", border_style="green", expand=True))

    elif step_type == "FINAL_ANSWER":
        console.print(Panel(
            Markdown(step.content),
            title=f"[bold green]{safe_title}[/bold green]",
            border_style="bold green",
            expand=True
        ))

    console.print()

def run_demonstration(query: str, auto_mode: bool = False, delay: float = 2.0, api_key: Optional[str] = None):
    mode = "openai" if api_key else "simulated"
    agent = SimpleAgent(mode=mode, api_key=api_key)

    console.print(f"[bold dim]⚙️ Engine Mode: [/bold dim][bold]{'Live OpenAI' if api_key else 'Simulator (Zero-Setup Video Mode)'}[/bold]")
    console.print(f"[bold dim]🎬 Presentation Mode: [/bold dim][bold]{'Auto-Play' if auto_mode else 'Interactive (Press Enter to advance)'}[/bold]\n")

    steps = list(agent.run_step_by_step(query))
    total_steps = len(steps)

    for i, step in enumerate(steps, 1):
        if not auto_mode and i > 1:
            try:
                input(f"👉 Press [Enter] to reveal Step {i}/{total_steps} (or Ctrl+C to stop)... ")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Demonstration paused.[/yellow]")
                break
        elif auto_mode and i > 1:
            with console.status(f"[dim]Pacing for video narration ({delay}s)...[/dim]"):
                time.sleep(delay)

        render_step(step, total_steps)

    console.print("[bold green]✨ Demonstration Complete![/bold green]")
    console.print("[dim]Use this step-by-step walkthrough in your presentation or video recording.[/dim]\n")

def main():
    parser = argparse.ArgumentParser(description="AI Agent Video Demonstration CLI")
    parser.add_argument("--auto", action="store_true", help="Auto-play steps without pressing Enter")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay in seconds between steps in auto mode")
    parser.add_argument("--api-key", type=str, default=None, help="Optional OpenAI API key for live LLM mode")
    args = parser.parse_args()

    print_banner()

    console.print("[bold]Select a Demo Scenario for your Video:[/bold]")
    for key, item in PRESET_SCENARIOS.items():
        console.print(f"  [bold cyan][{key}][/bold cyan] {item['title']}")
    console.print("  [bold cyan][4][/bold cyan] Custom Query (type your own goal)")
    console.print()

    choice = Prompt.ask("Choose scenario (1-4)", default="1")

    if choice in PRESET_SCENARIOS:
        selected = PRESET_SCENARIOS[choice]
        query = selected["query"]
        console.print(f"\n[green]Selected:[/green] {selected['title']}\n")
    else:
        query = Prompt.ask("\nEnter custom goal for agent", default="Calculate 250 * 18 with 5% tax")

    run_demonstration(query, auto_mode=args.auto, delay=args.delay, api_key=args.api_key)

if __name__ == "__main__":
    main()
