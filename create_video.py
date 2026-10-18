"""
create_video.py
Builds a complete educational MP4:
  - PPT-style slides
  - Live agent code execution with real outputs
  - Descriptions for every step
  - AI voiceover narration

Run:  python create_video.py
Output: video_assets/AI_Agent_Complete_Demo.mp4
"""

from __future__ import annotations

import asyncio
import json
import math
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np

from agent import SimpleAgent, AgentStep

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
OUT_DIR = ROOT / "video_assets"
FRAMES_DIR = OUT_DIR / "frames"
AUDIO_DIR = OUT_DIR / "audio"
VIDEO_PATH = OUT_DIR / "AI_Agent_Complete_Demo.mp4"
NARRATION_PATH = AUDIO_DIR / "FULL_VIDEO_NARRATION.mp3"

W, H = 1920, 1080
FPS = 24
VOICE = "en-US-JennyNeural"

# Colors (dark presentation look)
BG = (15, 23, 42)
CARD = (30, 41, 59)
ACCENT = (14, 165, 233)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)
GREEN = (16, 185, 129)
PURPLE = (139, 92, 246)
AMBER = (245, 158, 11)
CYAN = (6, 182, 212)
RED = (248, 113, 113)
CODE_BG = (2, 6, 23)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


FONT_XL = load_font(64, bold=True)
FONT_LG = load_font(44, bold=True)
FONT_MD = load_font(32, bold=True)
FONT_SM = load_font(26)
FONT_XS = load_font(22)
FONT_CODE = load_font(22)
try:
    FONT_CODE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 22)
except Exception:
    pass


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def new_canvas() -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # top accent bar
    draw.rectangle([0, 0, W, 8], fill=ACCENT)
    return img, draw


def rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def wrap_text(text: str, font, max_width: int) -> List[str]:
    words = text.split()
    lines, cur = [], ""
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for w in words:
        test = (cur + " " + w).strip()
        bbox = dummy.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def draw_wrapped(draw, text, xy, font, fill, max_width, line_gap=8):
    x, y = xy
    for line in wrap_text(text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def footer(draw, page: str):
    draw.text((60, H - 50), "AI Agent Step-by-Step Demo", font=FONT_XS, fill=MUTED)
    draw.text((W - 280, H - 50), page, font=FONT_XS, fill=MUTED)


# ---------------------------------------------------------------------------
# Slide / scene frame builders
# ---------------------------------------------------------------------------
def slide_title() -> Image.Image:
    img, draw = new_canvas()
    draw.text((W // 2, 280), "HOW AI AGENTS ACTUALLY WORK", font=FONT_XL, fill=WHITE, anchor="mm")
    draw.text(
        (W // 2, 380),
        "Step-by-Step Demo  |  ReAct Framework  |  Live Code Output",
        font=FONT_SM,
        fill=MUTED,
        anchor="mm",
    )
    rounded_rect(draw, (W // 2 - 220, 460, W // 2 + 220, 530), 12, ACCENT)
    draw.text((W // 2, 495), "COMPLETE VIDEO TUTORIAL", font=FONT_MD, fill=WHITE, anchor="mm")
    footer(draw, "01 / Title")
    return img


def slide_chatbot_vs_agent() -> Image.Image:
    img, draw = new_canvas()
    draw.text((60, 50), "Chatbot  vs  AI Agent", font=FONT_LG, fill=WHITE)

    # Left card
    rounded_rect(draw, (60, 160, 900, 820), 20, CARD)
    draw.text((100, 200), "CHATBOT", font=FONT_MD, fill=AMBER)
    for i, line in enumerate([
        "Prompt -> Text -> Stop",
        "No tools / no actions",
        "Cannot verify math",
        "Cannot look up live data",
        "Often hallucinates answers",
    ]):
        draw.text((100, 290 + i * 70), f"•  {line}", font=FONT_SM, fill=WHITE)

    # Right card
    rounded_rect(draw, (1020, 160, 1860, 820), 20, CARD)
    draw.text((1060, 200), "AI AGENT", font=FONT_MD, fill=GREEN)
    for i, line in enumerate([
        "Reason -> Act -> Observe -> Loop",
        "Uses tools as hands & eyes",
        "Safe calculator for exact math",
        "Knowledge base / APIs / weather",
        "Verified, grounded answers",
    ]):
        draw.text((1060, 290 + i * 70), f"•  {line}", font=FONT_SM, fill=WHITE)

    footer(draw, "02 / Concept")
    return img


def slide_react_loop() -> Image.Image:
    img, draw = new_canvas()
    draw.text((60, 50), "The ReAct Loop — 5 Steps", font=FONT_LG, fill=WHITE)

    steps = [
        ("1. GOAL", "User intent", ACCENT),
        ("2. THOUGHT", "LLM plans", CYAN),
        ("3. ACTION", "Call a tool", PURPLE),
        ("4. OBSERVE", "Read result", GREEN),
        ("5. ANSWER", "Final output", AMBER),
    ]
    box_w, box_h = 300, 220
    gap = 40
    total = 5 * box_w + 4 * gap
    start_x = (W - total) // 2
    y = 320
    for i, (label, desc, color) in enumerate(steps):
        x = start_x + i * (box_w + gap)
        rounded_rect(draw, (x, y, x + box_w, y + box_h), 18, color)
        draw.text((x + box_w // 2, y + 80), label, font=FONT_MD, fill=WHITE, anchor="mm")
        draw.text((x + box_w // 2, y + 140), desc, font=FONT_SM, fill=WHITE, anchor="mm")
        if i < 4:
            draw.text((x + box_w + gap // 2, y + box_h // 2), ">", font=FONT_LG, fill=MUTED, anchor="mm")

    draw.text(
        (W // 2, 660),
        "Thought → Action → Observation repeats until the goal is fully solved.",
        font=FONT_SM,
        fill=MUTED,
        anchor="mm",
    )
    footer(draw, "03 / Framework")
    return img


def slide_code(title: str, filename: str, code: str, description: str, page: str) -> Image.Image:
    img, draw = new_canvas()
    draw.text((60, 40), title, font=FONT_LG, fill=WHITE)
    draw.text((60, 110), description, font=FONT_SM, fill=MUTED)

    # Code panel
    rounded_rect(draw, (60, 180, W - 60, 920), 16, CODE_BG)
    draw.text((90, 200), filename, font=FONT_XS, fill=ACCENT)

    y = 250
    for line in code.splitlines()[:22]:
        # simple syntax tint
        color = WHITE
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith('"""'):
            color = MUTED
        elif stripped.startswith(("def ", "class ", "yield ", "return ", "from ", "import ")):
            color = CYAN
        elif "AgentStep" in line or "execute_tool" in line:
            color = GREEN
        draw.text((90, y), line[:110], font=FONT_CODE, fill=color)
        y += 28

    footer(draw, page)
    return img


def slide_goal(query: str) -> Image.Image:
    img, draw = new_canvas()
    draw.text((60, 50), "Demo Goal — Live Agent Input", font=FONT_LG, fill=WHITE)
    rounded_rect(draw, (120, 280, W - 120, 560), 20, CARD)
    draw.text((160, 320), "USER GOAL", font=FONT_MD, fill=AMBER)
    draw_wrapped(draw, f'"{query}"', (160, 400), FONT_SM, WHITE, W - 360)
    draw.text(
        (120, 640),
        "Why this is a great agent demo: needs policy lookup + exact math + multi-step reasoning.",
        font=FONT_SM,
        fill=MUTED,
    )
    footer(draw, "04 / Goal")
    return img


def slide_agent_step(step: AgentStep, scenario_label: str, page: str) -> Image.Image:
    img, draw = new_canvas()

    color_map = {
        "GOAL": AMBER,
        "THOUGHT": CYAN,
        "ACTION": PURPLE,
        "OBSERVATION": GREEN,
        "FINAL_ANSWER": AMBER,
    }
    accent = color_map.get(step.step_type, ACCENT)

    draw.text((60, 40), scenario_label, font=FONT_XS, fill=MUTED)
    draw.text((60, 85), step.title.replace("🎯", "").replace("🧠", "").replace("🛠️", "")
              .replace("👁️", "").replace("✅", "").strip(), font=FONT_LG, fill=WHITE)

    # Type badge
    badge = step.step_type
    tw = draw.textbbox((0, 0), badge, font=FONT_XS)
    bw = (tw[2] - tw[0]) + 40
    rounded_rect(draw, (60, 160, 60 + bw, 210), 10, accent)
    draw.text((80, 172), badge, font=FONT_XS, fill=WHITE)

    # Main content card
    rounded_rect(draw, (60, 240, W - 60, 720), 18, CARD)
    content = step.content
    if step.step_type == "FINAL_ANSWER":
        # strip markdown-ish
        content = content.replace("### ", "").replace("**", "").replace("*", "")
    y = draw_wrapped(draw, content, (100, 280), FONT_SM, WHITE, W - 220, line_gap=10)

    if step.tool_name:
        draw.text((100, min(y + 30, 640)), f"Tool: {step.tool_name}", font=FONT_XS, fill=PURPLE)
        if step.tool_args:
            args = json.dumps(step.tool_args)
            draw.text((100, min(y + 70, 680)), f"Args: {args[:120]}", font=FONT_CODE, fill=MUTED)

    # Description strip
    rounded_rect(draw, (60, 760, W - 60, 960), 16, (20, 30, 48))
    draw.text((100, 790), "DESCRIPTION", font=FONT_XS, fill=ACCENT)
    desc = step.explanation or "Agent continues the ReAct loop."
    draw_wrapped(draw, desc, (100, 840), FONT_SM, MUTED, W - 220)

    footer(draw, page)
    return img


def slide_terminal_output(title: str, lines: List[str], description: str, page: str) -> Image.Image:
    img, draw = new_canvas()
    draw.text((60, 40), title, font=FONT_LG, fill=WHITE)
    draw_wrapped(draw, description, (60, 110), FONT_SM, MUTED, W - 140)

    rounded_rect(draw, (60, 200, W - 60, 940), 16, CODE_BG)
    # fake terminal chrome
    draw.ellipse([90, 220, 115, 245], fill=RED)
    draw.ellipse([130, 220, 155, 245], fill=AMBER)
    draw.ellipse([170, 220, 195, 245], fill=GREEN)
    draw.text((230, 220), "python cli_demo.py --auto", font=FONT_XS, fill=MUTED)

    y = 280
    for line in lines[:20]:
        color = GREEN if any(k in line for k in ("FINAL", "Result", "Observation", "$")) else WHITE
        if "THOUGHT" in line or "Reasoning" in line:
            color = CYAN
        if "ACTION" in line or "Tool" in line:
            color = PURPLE
        draw.text((90, y), line[:115], font=FONT_CODE, fill=color)
        y += 30

    footer(draw, page)
    return img


def slide_summary(results: List[Tuple[str, str]]) -> Image.Image:
    img, draw = new_canvas()
    draw.text((60, 50), "Live Results Summary", font=FONT_LG, fill=WHITE)
    y = 160
    for title, value in results:
        rounded_rect(draw, (60, y, W - 60, y + 160), 16, CARD)
        draw.text((100, y + 30), title, font=FONT_MD, fill=ACCENT)
        draw_wrapped(draw, value, (100, y + 85), FONT_SM, WHITE, W - 220)
        y += 190
    footer(draw, "Summary")
    return img


def slide_outro() -> Image.Image:
    img, draw = new_canvas()
    draw.text((W // 2, 360), "That's How an AI Agent Works", font=FONT_XL, fill=WHITE, anchor="mm")
    draw.text(
        (W // 2, 460),
        "Reason  →  Act  →  Observe  →  Answer",
        font=FONT_MD,
        fill=ACCENT,
        anchor="mm",
    )
    draw.text(
        (W // 2, 560),
        "Code: agent.py  ·  tools.py  ·  cli_demo.py  ·  app.py",
        font=FONT_SM,
        fill=MUTED,
        anchor="mm",
    )
    draw.text((W // 2, 680), "Thanks for watching!", font=FONT_LG, fill=GREEN, anchor="mm")
    footer(draw, "End")
    return img


# ---------------------------------------------------------------------------
# Capture live agent outputs
# ---------------------------------------------------------------------------
def run_scenarios() -> dict:
    agent = SimpleAgent(mode="simulated")
    scenarios = {
        "finance": "Calculate the total for an order of 50 units at $30 each, apply the VIP discount, and add 8% sales tax.",
        "weather": "Check the current weather in Tokyo and convert the temperature to Fahrenheit.",
        "support": "A customer wants to return a $200 item purchased 45 days ago. Check the policy and calculate the refund.",
    }
    results = {}
    for key, query in scenarios.items():
        steps = list(agent.run_step_by_step(query))
        results[key] = {"query": query, "steps": steps}
        print(f"[RUN] {key}: {len(steps)} steps captured")
    return results


def steps_to_terminal_lines(steps: List[AgentStep]) -> List[str]:
    lines = []
    for s in steps:
        prefix = {
            "GOAL": "[GOAL]",
            "THOUGHT": "[THINK]",
            "ACTION": "[ACT ]",
            "OBSERVATION": "[OBS ]",
            "FINAL_ANSWER": "[DONE]",
        }.get(s.step_type, "[STEP]")
        text = s.content.replace("\n", " ")[:95]
        lines.append(f"{prefix} {text}")
    return lines


def narrate_step(step: AgentStep, label: str) -> str:
    """Short spoken description for each live agent step."""
    content = step.content.replace("### ", "").replace("**", "").replace("\n", " ").strip()
    content = content[:220]
    if step.step_type == "GOAL":
        return f"In the {label} demo, the goal is received. {content}"
    if step.step_type == "THOUGHT":
        return f"The agent is thinking. {content}"
    if step.step_type == "ACTION":
        tool = step.tool_name or "a tool"
        return f"Now the agent takes action and calls the {tool} tool. {content}"
    if step.step_type == "OBSERVATION":
        return f"Here is the tool observation. {content}"
    if step.step_type == "FINAL_ANSWER":
        return f"Final answer for {label}. {content}"
    return content


# ---------------------------------------------------------------------------
# Narration
# ---------------------------------------------------------------------------
NARRATION_SCRIPTS = {
    "title": (
        "Welcome. In this complete video, we will build and run a real AI Agent step by step. "
        "You will see PowerPoint style slides, live Python code execution, and the exact outputs "
        "produced by the agent."
    ),
    "concept": (
        "A chatbot only generates text. An AI Agent reasons, calls tools, observes the results, "
        "and loops until the job is done. That is the ReAct framework — Reasoning plus Acting."
    ),
    "framework": (
        "Every agent follows five steps: Goal, Thought, Action, Observation, and Final Answer. "
        "Thought, Action and Observation can repeat many times."
    ),
    "code_tools": (
        "Here is tools.py. These are the agent's hands. We have a safe calculator, a weather lookup, "
        "a knowledge base search, and currency conversion. The agent never invents tool results — "
        "it executes real Python functions."
    ),
    "code_agent": (
        "Here is agent.py. The SimpleAgent class runs the ReAct loop. For every user goal, "
        "it yields a Goal step, then Thought, Action, Observation, and finally a verified answer."
    ),
    "goal_finance": (
        "Demo number one. The user goal is: calculate the total for fifty units at thirty dollars each, "
        "apply the VIP discount, and add eight percent sales tax."
    ),
    "run_finance": (
        "Watch the live run. First the agent thinks and realizes it must look up the VIP discount. "
        "It calls search knowledge base. The tool returns twenty percent discount. "
        "Then it calls the calculator with the exact expression. The result is one thousand two hundred ninety six dollars."
    ),
    "goal_weather": (
        "Demo number two. The agent must check the weather in Tokyo and convert Celsius to Fahrenheit."
    ),
    "run_weather": (
        "It calls get weather for Tokyo, observes the temperature, then uses the calculator to convert "
        "Celsius to Fahrenheit using the formula C times nine divided by five, plus thirty two."
    ),
    "goal_support": (
        "Demo number three. A customer wants to return a two hundred dollar item after forty five days."
    ),
    "run_support": (
        "The agent looks up the return policy. Returns between thirty one and sixty days have a fifteen percent "
        "restocking fee. It calculates the refund as one hundred seventy dollars."
    ),
    "summary": (
        "All three demos completed successfully. Finance total one thousand two hundred ninety six dollars. "
        "Tokyo weather converted correctly. Customer refund one hundred seventy dollars. "
        "Zero hallucinations — every number came from a tool."
    ),
    "outro": (
        "That is how an AI Agent works from the inside out. Reason, act, observe, answer. "
        "You now have the full project: agent.py, tools.py, the CLI demo, the Streamlit app, slides, and this video. "
        "Thanks for watching!"
    ),
}


async def synthesize_narration(scripts: dict) -> AudioSegment:
    import edge_tts

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    combined = AudioSegment.silent(duration=400)
    for key, text in scripts.items():
        out = AUDIO_DIR / f"vid_{key}.mp3"
        print(f"[TTS] {key}...")
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(str(out))
        segment = AudioSegment.from_mp3(str(out))
        combined += segment + AudioSegment.silent(duration=600)
    combined.export(str(NARRATION_PATH), format="mp3")
    print(f"[OK] Narration -> {NARRATION_PATH}")
    return combined


# ---------------------------------------------------------------------------
# Timeline: frames + durations synced to narration segments
# ---------------------------------------------------------------------------
def build_timeline(results: dict) -> List[Tuple[Image.Image, str]]:
    """Return list of (frame, narration_key) in order."""
    timeline = []

    tools_code = textwrap.dedent('''\
        def calculator(expression: str) -> str:
            """Safe math — no LLM hallucinations."""
            ...

        def get_weather(city: str) -> str:
            """Live weather for any city."""
            ...

        def search_knowledge_base(query: str) -> str:
            """VIP discount, return policy, products."""
            ...

        TOOL_REGISTRY = {
            "calculator": calculator,
            "get_weather": get_weather,
            "search_knowledge_base": search_knowledge_base,
        }
    ''')

    agent_code = textwrap.dedent('''\
        class SimpleAgent:
            def run_step_by_step(self, user_query: str):
                yield AgentStep(step_type="GOAL", content=user_query)
                # Thought -> Action -> Observation loop
                yield AgentStep(step_type="THOUGHT", ...)
                yield AgentStep(step_type="ACTION", tool_name=...)
                result = execute_tool(tool_name, **args)
                yield AgentStep(step_type="OBSERVATION", content=result)
                yield AgentStep(step_type="FINAL_ANSWER", ...)
    ''')

    timeline.append((slide_title(), "title"))
    timeline.append((slide_chatbot_vs_agent(), "concept"))
    timeline.append((slide_react_loop(), "framework"))
    timeline.append((
        slide_code(
            "Code Walkthrough — tools.py",
            "tools.py",
            tools_code,
            "DESCRIPTION: Real Python functions the agent can call as tools.",
            "05 / Code",
        ),
        "code_tools",
    ))
    timeline.append((
        slide_code(
            "Code Walkthrough — agent.py",
            "agent.py",
            agent_code,
            "DESCRIPTION: The ReAct loop yields every step so we can display it live.",
            "06 / Code",
        ),
        "code_agent",
    ))

    def add_scenario(timeline, results_key, label, page_prefix, goal_key, overview_key, step_prefix):
        data = results[results_key]
        timeline.append((slide_goal(data["query"]), goal_key))
        timeline.append((
            slide_terminal_output(
                f"Live Run — {label}",
                steps_to_terminal_lines(data["steps"]),
                "DESCRIPTION: Actual output from SimpleAgent.run_step_by_step() — live Python execution.",
                f"{page_prefix} / Live Run",
            ),
            overview_key,
        ))
        for i, step in enumerate(data["steps"]):
            narr_key = f"{step_prefix}_{i}"
            # Dynamic short narration text stored for TTS generation
            NARRATION_SCRIPTS[narr_key] = narrate_step(step, label)
            timeline.append((
                slide_agent_step(step, f"SCENARIO · {label} · Live Output", f"{page_prefix}.{i+1}"),
                narr_key,
            ))

    add_scenario(timeline, "finance", "Financial Analyst", "07", "goal_finance", "run_finance", "fin")
    add_scenario(timeline, "weather", "Travel Assistant", "08", "goal_weather", "run_weather", "wth")
    add_scenario(timeline, "support", "Customer Support", "09", "goal_support", "run_support", "sup")

    # Summary from final answers
    finals = []
    for key, label in [("finance", "Finance Total"), ("weather", "Tokyo Weather"), ("support", "Refund Amount")]:
        final = [st for st in results[key]["steps"] if st.step_type == "FINAL_ANSWER"][0]
        clean = final.content.replace("### ", "").replace("**", "").replace("\n", " ")[:180]
        finals.append((label, clean))
    timeline.append((slide_summary(finals), "summary"))
    timeline.append((slide_outro(), "outro"))
    return timeline


# ---------------------------------------------------------------------------
# Render video
# ---------------------------------------------------------------------------
def render_video(timeline: List[Tuple[Image.Image, str]], audio_segments: dict):
    """Each timeline entry gets its own narration audio + matching frame duration."""
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    clips: List[Tuple[Image.Image, int]] = []
    full_audio = AudioSegment.silent(duration=0)

    for img, key in timeline:
        if key not in audio_segments:
            raise KeyError(f"Missing narration audio for key: {key}")
        seg = audio_segments[key]
        duration_ms = len(seg) + 350
        clips.append((img, duration_ms))
        full_audio += seg + AudioSegment.silent(duration=350)

    audio_out = AUDIO_DIR / "video_timeline_audio.mp3"
    full_audio.export(str(audio_out), format="mp3")
    print(f"[OK] Timeline audio -> {audio_out} ({len(full_audio)/1000:.1f}s)")

    # Write frames as PNG sequence then encode with ffmpeg (more reliable + faster mux)
    print("[RENDER] Saving scene images...")
    frame_paths = []
    concat_list = OUT_DIR / "ffmpeg_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for idx, (img, duration_ms) in enumerate(clips):
            path = FRAMES_DIR / f"scene_{idx:03d}.png"
            img.save(path, "PNG")
            frame_paths.append(path)
            # Relative path from OUT_DIR (avoids Windows space/quote issues)
            rel = f"frames/scene_{idx:03d}.png"
            f.write(f"file '{rel}'\n")
            f.write(f"duration {duration_ms / 1000.0:.3f}\n")
            if idx % 8 == 0:
                print(f"  saved scene {idx+1}/{len(clips)}")
        # Repeat last file once (ffmpeg concat requirement)
        last_rel = f"frames/scene_{len(frame_paths)-1:03d}.png"
        f.write(f"file '{last_rel}'\n")

    raw_video = OUT_DIR / "raw_video_no_audio.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    print("[RENDER] Encoding video with ffmpeg...")
    cmd_vid = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list.name,
        "-vf", f"fps={FPS}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        str(raw_video.name),
    ]
    result = subprocess.run(cmd_vid, capture_output=True, text=True, cwd=str(OUT_DIR))
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError("ffmpeg video encode failed")
    print(f"[OK] Raw video -> {raw_video}")

    print("[MUX] Combining video + audio...")
    cmd = [
        ffmpeg, "-y",
        "-i", str(raw_video.name),
        "-i", str(Path("audio") / audio_out.name),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(VIDEO_PATH.name),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(OUT_DIR))
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError("ffmpeg mux failed")
    print(f"[DONE] Final video -> {VIDEO_PATH}")

    try:
        raw_video.unlink()
    except Exception:
        pass
    return VIDEO_PATH


async def prepare_audio_segments() -> dict:
    import edge_tts

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    segments = {}
    for key, text in NARRATION_SCRIPTS.items():
        out = AUDIO_DIR / f"vid_{key}.mp3"
        if not out.exists():
            print(f"[TTS] Generating {key}...")
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(str(out))
        else:
            print(f"[TTS] Reusing {key}")
        segments[key] = AudioSegment.from_mp3(str(out))
    return segments


def main():
    print("=" * 64)
    print(" Creating COMPLETE demo video (slides + live code + narration)")
    print("=" * 64)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/4] Running agent scenarios (live code)...")
    results = run_scenarios()

    print("\n[2/4] Building slide timeline from PPT + live outputs...")
    timeline = build_timeline(results)
    print(f"  {len(timeline)} scenes prepared")

    print("\n[3/4] Generating / loading narration audio...")
    audio_segments = asyncio.run(prepare_audio_segments())

    print("\n[4/4] Rendering MP4 (this may take a few minutes)...")
    path = render_video(timeline, audio_segments)

    size_mb = path.stat().st_size / (1024 * 1024)
    print()
    print("=" * 64)
    print(f" SUCCESS -> {path}")
    print(f" Size    -> {size_mb:.1f} MB")
    print("=" * 64)


if __name__ == "__main__":
    main()
