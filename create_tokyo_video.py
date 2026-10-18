"""
create_tokyo_video.py
Focused educational video: Tokyo Weather AI Agent
- Functional explanation (what it does for the user)
- Technical explanation (how the agent is built & how ReAct works)
- Live code execution with real outputs of every step

Run:  python create_tokyo_video.py
Out:  video_assets/Tokyo_Weather_Agent_Demo.mp4
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
import imageio_ffmpeg

from agent import SimpleAgent, AgentStep
from tools import get_weather, calculator, execute_tool

# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
OUT_DIR = ROOT / "video_assets"
FRAMES_DIR = OUT_DIR / "tokyo_frames"
AUDIO_DIR = OUT_DIR / "tokyo_audio"
VIDEO_PATH = OUT_DIR / "Tokyo_Weather_Agent_Demo.mp4"

W, H = 1920, 1080
FPS = 24
VOICE = "en-US-JennyNeural"

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

QUERY = "Check the current weather in Tokyo and convert the temperature to Fahrenheit."

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def load_font(size: int, bold: bool = False):
    paths = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


FONT_XL = load_font(58, True)
FONT_LG = load_font(40, True)
FONT_MD = load_font(30, True)
FONT_SM = load_font(24)
FONT_XS = load_font(20)
try:
    FONT_CODE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 22)
except Exception:
    FONT_CODE = FONT_XS


def new_canvas():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 8], fill=ACCENT)
    return img, draw


def rounded(draw, xy, r, fill):
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def wrap(text, font, max_w):
    words = str(text).split()
    lines, cur = [], ""
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for w in words:
        test = (cur + " " + w).strip()
        if dummy.textbbox((0, 0), test, font=font)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def draw_wrap(draw, text, xy, font, fill, max_w, gap=8):
    x, y = xy
    for line in wrap(text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        h = draw.textbbox((0, 0), line, font=font)[3]
        y += h + gap
    return y


def footer(draw, page):
    draw.text((60, H - 48), "Tokyo Weather AI Agent  |  Technical + Functional Demo", font=FONT_XS, fill=MUTED)
    draw.text((W - 220, H - 48), page, font=FONT_XS, fill=MUTED)


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------
def slide_title():
    img, d = new_canvas()
    d.text((W // 2, 260), "TOKYO WEATHER AI AGENT", font=FONT_XL, fill=WHITE, anchor="mm")
    d.text((W // 2, 350), "How an Agent is Created  ·  How it Works  ·  Live Run", font=FONT_SM, fill=MUTED, anchor="mm")
    rounded(d, (W // 2 - 280, 430, W // 2 + 280, 510), 14, ACCENT)
    d.text((W // 2, 470), "FUNCTIONAL + TECHNICAL WALKTHROUGH", font=FONT_MD, fill=WHITE, anchor="mm")
    d.text((W // 2, 600), f'Goal: "{QUERY}"', font=FONT_SM, fill=CYAN, anchor="mm")
    footer(d, "01")
    return img


def slide_functional():
    img, d = new_canvas()
    d.text((60, 40), "FUNCTIONAL VIEW — What Does This Agent Do?", font=FONT_LG, fill=WHITE)
    items = [
        ("User Goal", "Ask for Tokyo weather AND Fahrenheit conversion in one sentence."),
        ("Agent Behavior", "Breaks the goal into steps: fetch weather, then convert units."),
        ("Tools Used", "1) get_weather(city)   2) calculator(expression)"),
        ("User Outcome", "A clear weather report with Celsius and Fahrenheit — no guessing."),
        ("Why an Agent?", "A chatbot might invent the temperature. This agent calls real tools."),
    ]
    y = 140
    for title, desc in items:
        rounded(d, (60, y, W - 60, y + 130), 14, CARD)
        d.text((100, y + 25), title, font=FONT_MD, fill=ACCENT)
        draw_wrap(d, desc, (100, y + 70), FONT_SM, WHITE, W - 220)
        y += 150
    footer(d, "02 / Functional")
    return img


def slide_architecture():
    img, d = new_canvas()
    d.text((60, 40), "TECHNICAL VIEW — Agent Architecture", font=FONT_LG, fill=WHITE)

    boxes = [
        (80, 180, 420, 380, "1. USER", "Natural language\ngoal", AMBER),
        (500, 180, 840, 380, "2. AGENT", "SimpleAgent\nReAct loop", ACCENT),
        (920, 180, 1260, 380, "3. TOOLS", "weather +\ncalculator", PURPLE),
        (1340, 180, 1840, 380, "4. ANSWER", "Verified\nreport", GREEN),
    ]
    for x1, y1, x2, y2, title, body, color in boxes:
        rounded(d, (x1, y1, x2, y2), 16, color)
        d.text(((x1 + x2) // 2, y1 + 55), title, font=FONT_MD, fill=WHITE, anchor="mm")
        for i, line in enumerate(body.split("\n")):
            d.text(((x1 + x2) // 2, y1 + 120 + i * 36), line, font=FONT_SM, fill=WHITE, anchor="mm")

    d.text((W // 2, 460), "Data flow: Goal → Thought → Action → Observation → (repeat) → Final Answer", font=FONT_SM, fill=MUTED, anchor="mm")

    # File map
    rounded(d, (60, 520, W - 60, 960), 16, CARD)
    d.text((100, 550), "PROJECT FILES (how the agent is created)", font=FONT_MD, fill=CYAN)
    lines = [
        "tools.py   →  define get_weather() and calculator() + TOOL_REGISTRY",
        "agent.py   →  SimpleAgent class implements the ReAct step-by-step loop",
        "cli_demo.py / app.py  →  present each step for demos and videos",
        "This video captures a live call: SimpleAgent().run_step_by_step(query)",
    ]
    y = 620
    for line in lines:
        d.text((100, y), line, font=FONT_CODE, fill=WHITE)
        y += 55
    footer(d, "03 / Architecture")
    return img


def slide_code(title, filename, code, description, page):
    img, d = new_canvas()
    d.text((60, 35), title, font=FONT_LG, fill=WHITE)
    draw_wrap(d, description, (60, 100), FONT_SM, MUTED, W - 140)
    rounded(d, (60, 180, W - 60, 960), 16, CODE_BG)
    d.text((90, 200), filename, font=FONT_XS, fill=ACCENT)
    y = 250
    for line in code.splitlines()[:20]:
        color = MUTED if line.strip().startswith(("#", '"""', "'''")) else WHITE
        if line.lstrip().startswith(("def ", "class ", "yield ", "return ")):
            color = CYAN
        if "execute_tool" in line or "get_weather" in line or "calculator" in line:
            color = GREEN
        d.text((90, y), line[:110], font=FONT_CODE, fill=color)
        y += 32
    footer(d, page)
    return img


def slide_react_detail():
    img, d = new_canvas()
    d.text((60, 40), "TECHNICAL — ReAct Loop Explained", font=FONT_LG, fill=WHITE)
    steps = [
        ("GOAL", "Agent receives the Tokyo weather + Fahrenheit request.", AMBER),
        ("THOUGHT", "LLM/planner decides: first I need live weather data for Tokyo.", CYAN),
        ("ACTION", "Calls tool get_weather(city='Tokyo').", PURPLE),
        ("OBSERVATION", "Tool returns real temperature in Celsius + conditions.", GREEN),
        ("THOUGHT 2", "Now convert C to F using formula (C × 9/5) + 32.", CYAN),
        ("ACTION 2", "Calls calculator with that exact expression.", PURPLE),
        ("OBSERVATION 2", "Calculator returns precise Fahrenheit value.", GREEN),
        ("FINAL ANSWER", "Agent writes a complete weather report for the user.", AMBER),
    ]
    y = 120
    for name, desc, color in steps:
        rounded(d, (60, y, 320, y + 85), 10, color)
        d.text((190, y + 42), name, font=FONT_XS, fill=WHITE, anchor="mm")
        d.text((360, y + 28), desc, font=FONT_SM, fill=WHITE)
        y += 100
    footer(d, "06 / ReAct")
    return img


def slide_tool_live(tool_name, args, result, description, page):
    img, d = new_canvas()
    d.text((60, 40), f"LIVE TOOL EXECUTION — {tool_name}", font=FONT_LG, fill=WHITE)
    draw_wrap(d, description, (60, 110), FONT_SM, MUTED, W - 140)

    rounded(d, (60, 200, W - 60, 420), 16, CARD)
    d.text((100, 230), "INPUT (function call)", font=FONT_MD, fill=PURPLE)
    d.text((100, 300), f"{tool_name}({json.dumps(args)})", font=FONT_CODE, fill=WHITE)

    rounded(d, (60, 460, W - 60, 780), 16, CARD)
    d.text((100, 490), "OUTPUT (observation returned to agent)", font=FONT_MD, fill=GREEN)
    draw_wrap(d, str(result), (100, 560), FONT_SM, WHITE, W - 220)

    rounded(d, (60, 820, W - 60, 960), 14, (20, 30, 48))
    d.text((100, 860), "TECHNICAL NOTE: The LLM does not invent this value — Python executes the tool.", font=FONT_SM, fill=CYAN)
    footer(d, page)
    return img


def slide_step(step: AgentStep, idx: int, total: int):
    img, d = new_canvas()
    colors = {
        "GOAL": AMBER, "THOUGHT": CYAN, "ACTION": PURPLE,
        "OBSERVATION": GREEN, "FINAL_ANSWER": AMBER,
    }
    accent = colors.get(step.step_type, ACCENT)
    d.text((60, 35), f"LIVE AGENT RUN  ·  Step {idx}/{total}", font=FONT_XS, fill=MUTED)
    title = step.title
    for e in ("🎯", "🧠", "🛠️", "👁️", "✅"):
        title = title.replace(e, "")
    d.text((60, 80), title.strip(), font=FONT_LG, fill=WHITE)

    tw = d.textbbox((0, 0), step.step_type, font=FONT_XS)
    rounded(d, (60, 155, 60 + (tw[2] - tw[0]) + 36, 205), 10, accent)
    d.text((78, 168), step.step_type, font=FONT_XS, fill=WHITE)

    rounded(d, (60, 240, W - 60, 700), 16, CARD)
    content = step.content.replace("### ", "").replace("**", "").replace("*", "")
    draw_wrap(d, content, (100, 280), FONT_SM, WHITE, W - 220, gap=10)

    if step.tool_name:
        d.text((100, 620), f"Tool: {step.tool_name}   Args: {json.dumps(step.tool_args or {})}", font=FONT_CODE, fill=PURPLE)

    rounded(d, (60, 740, W - 60, 960), 14, (20, 30, 48))
    d.text((100, 770), "DESCRIPTION (Functional + Technical)", font=FONT_XS, fill=ACCENT)
    draw_wrap(d, step.explanation or "Agent continues the ReAct loop.", (100, 820), FONT_SM, MUTED, W - 220)
    footer(d, f"Live {idx}/{total}")
    return img


def slide_summary(temp_c, temp_f, weather_text):
    img, d = new_canvas()
    d.text((60, 40), "RESULT + WHAT YOU LEARNED", font=FONT_LG, fill=WHITE)

    rounded(d, (60, 140, W - 60, 360), 16, CARD)
    d.text((100, 170), "FUNCTIONAL RESULT", font=FONT_MD, fill=GREEN)
    draw_wrap(d, weather_text, (100, 230), FONT_SM, WHITE, W - 220)
    d.text((100, 300), f"Temperature: {temp_c}°C  =  {temp_f}°F", font=FONT_MD, fill=AMBER)

    rounded(d, (60, 400, W - 60, 960), 16, CARD)
    d.text((100, 430), "TECHNICAL TAKEAWAYS", font=FONT_MD, fill=ACCENT)
    points = [
        "1. Create tools as plain Python functions and register them.",
        "2. Create an agent loop that yields Thought → Action → Observation.",
        "3. Always execute tools for facts/math — never trust LLM arithmetic.",
        "4. Feed tool results back into the next Thought (memory / context).",
        "5. Stop when the goal is complete and synthesize a Final Answer.",
        "6. Same pattern scales to APIs, databases, bookings, and workflows.",
    ]
    y = 500
    for p in points:
        d.text((100, y), p, font=FONT_SM, fill=WHITE)
        y += 55
    footer(d, "Summary")
    return img


def slide_outro():
    img, d = new_canvas()
    d.text((W // 2, 340), "Tokyo Weather Agent — Complete", font=FONT_XL, fill=WHITE, anchor="mm")
    d.text((W // 2, 440), "Create tools  →  Build ReAct loop  →  Run  →  Observe  →  Answer", font=FONT_MD, fill=ACCENT, anchor="mm")
    d.text((W // 2, 540), "Files: tools.py  ·  agent.py  ·  create_tokyo_video.py", font=FONT_SM, fill=MUTED, anchor="mm")
    d.text((W // 2, 660), "Thanks for watching!", font=FONT_LG, fill=GREEN, anchor="mm")
    footer(d, "End")
    return img


# ---------------------------------------------------------------------------
# Narration
# ---------------------------------------------------------------------------
SCRIPTS = {
    "title": (
        "Welcome to the Tokyo Weather AI Agent demo. In this short video we capture everything: "
        "the functional purpose of the agent, the technical design, how the agent is created in code, "
        "and a full live run with real tool outputs."
    ),
    "functional": (
        "Functionally, the agent solves a multi-step user goal. The user asks for Tokyo weather and also "
        "wants the temperature in Fahrenheit. A normal chatbot might invent numbers. This agent uses tools "
        "to fetch weather and calculate the conversion, then returns a verified report."
    ),
    "architecture": (
        "Technically, the system has four parts: the user goal, the SimpleAgent ReAct loop, the tool registry "
        "with weather and calculator functions, and the final answer. The agent is created as Python modules: "
        "tools.py for tools, and agent.py for the reasoning loop."
    ),
    "code_tools": (
        "Here is how tools are created. get_weather takes a city and returns temperature and conditions. "
        "calculator safely evaluates a math expression. Both are registered so the agent can call them by name."
    ),
    "code_agent": (
        "Here is how the agent is created. SimpleAgent.run_step_by_step yields each ReAct stage: Goal, Thought, "
        "Action, Observation, and Final Answer. That generator is what lets us capture and display every step."
    ),
    "react": (
        "The ReAct loop for Tokyo works like this: receive the goal, think that weather data is needed, "
        "call get_weather, observe Celsius, think about the Fahrenheit formula, call calculator, observe the result, "
        "then write the final weather report."
    ),
    "tool_weather": (
        "Now we execute the weather tool live. We call get_weather with city Tokyo. "
        "The observation returns the real Celsius temperature and conditions back to the agent."
    ),
    "tool_calc": (
        "Next we execute the calculator live. We evaluate the conversion formula Celsius times nine divided by five, "
        "plus thirty two. The agent never guesses Fahrenheit — the tool computes it."
    ),
    "live_intro": (
        "Now watch the complete live agent run. Every panel is a real step produced by SimpleAgent on the Tokyo query."
    ),
    "summary": (
        "Functional result: a verified Tokyo weather report with Celsius and Fahrenheit. "
        "Technical takeaway: create tools as functions, build a ReAct loop, execute tools for facts, "
        "feed observations back into thought, and finish with a synthesized answer."
    ),
    "outro": (
        "That is how a Tokyo Weather AI Agent is created and how it works end to end. "
        "Thank you for watching!"
    ),
}


def narrate_step(step: AgentStep, i: int) -> str:
    c = step.content.replace("### ", "").replace("**", "").replace("\n", " ")[:200]
    if step.step_type == "GOAL":
        return f"Step {i}. Goal received. {c}"
    if step.step_type == "THOUGHT":
        return f"Step {i}. The agent thinks. {c}"
    if step.step_type == "ACTION":
        return f"Step {i}. Action. Calling tool {step.tool_name}. {c}"
    if step.step_type == "OBSERVATION":
        return f"Step {i}. Observation from the tool. {c}"
    if step.step_type == "FINAL_ANSWER":
        return f"Step {i}. Final answer synthesized. {c}"
    return c


# ---------------------------------------------------------------------------
# Build + render
# ---------------------------------------------------------------------------
def build_timeline(steps: List[AgentStep]) -> List[Tuple[Image.Image, str]]:
    tools_code = textwrap.dedent('''\
        def get_weather(city: str) -> str:
            """Fetch weather for a city."""
            info = WEATHER_DATABASE[city.lower()]
            return f"{info['temperature_c']} C, {info['condition']}"

        def calculator(expression: str) -> str:
            """Safe math evaluator — no LLM guessing."""
            return str(eval_safe(expression))

        # Register tools so the agent can call them by name
        TOOL_REGISTRY = {
            "get_weather": get_weather,
            "calculator": calculator,
        }
    ''')

    agent_code = textwrap.dedent('''\
        class SimpleAgent:
            def run_step_by_step(self, user_query: str):
                yield AgentStep("GOAL", user_query)

                # Thought 1: need Tokyo weather
                yield AgentStep("THOUGHT", "Fetch weather first")
                result = execute_tool("get_weather", city="Tokyo")
                yield AgentStep("ACTION", tool="get_weather")
                yield AgentStep("OBSERVATION", result)

                # Thought 2: convert C -> F
                f = execute_tool("calculator", expression="(18*9/5)+32")
                yield AgentStep("FINAL_ANSWER", report)
    ''')

    tl: List[Tuple[Image.Image, str]] = []
    tl.append((slide_title(), "title"))
    tl.append((slide_functional(), "functional"))
    tl.append((slide_architecture(), "architecture"))
    tl.append((slide_code(
        "CREATE TOOLS — tools.py",
        "tools.py",
        tools_code,
        "TECHNICAL: Tools are ordinary Python functions. The agent calls them instead of inventing facts.",
        "04 / tools.py",
    ), "code_tools"))
    tl.append((slide_code(
        "CREATE AGENT — agent.py",
        "agent.py",
        agent_code,
        "TECHNICAL: SimpleAgent yields every ReAct step so demos and videos can show the full loop.",
        "05 / agent.py",
    ), "code_agent"))
    tl.append((slide_react_detail(), "react"))

    # Live tool calls (actual execution)
    weather_out = execute_tool("get_weather", city="Tokyo")
    temp_c = 18
    calc_expr = f"({temp_c} * 9 / 5) + 32"
    calc_out = execute_tool("calculator", expression=calc_expr)

    tl.append((slide_tool_live(
        "get_weather",
        {"city": "Tokyo"},
        weather_out,
        "FUNCTIONAL: Get current Tokyo conditions. TECHNICAL: Direct Python function call via execute_tool().",
        "07 / Tool Live",
    ), "tool_weather"))
    tl.append((slide_tool_live(
        "calculator",
        {"expression": calc_expr},
        f"{calc_out} °F",
        "FUNCTIONAL: Convert Celsius to Fahrenheit. TECHNICAL: Exact arithmetic outside the LLM.",
        "08 / Tool Live",
    ), "tool_calc"))

    # Full agent run
    # Intro narration then each step
    SCRIPTS["live_intro"] = SCRIPTS["live_intro"]  # ensure present
    # Use first step key for intro by inserting a title-like step frame
    intro_img, d = new_canvas()
    d.text((W // 2, 400), "LIVE FULL AGENT RUN", font=FONT_XL, fill=WHITE, anchor="mm")
    d.text((W // 2, 500), "Capturing every Thought, Action, Observation from SimpleAgent", font=FONT_SM, fill=MUTED, anchor="mm")
    footer(d, "09 / Live")
    tl.append((intro_img, "live_intro"))

    for i, step in enumerate(steps, 1):
        key = f"step_{i}"
        SCRIPTS[key] = narrate_step(step, i)
        tl.append((slide_step(step, i, len(steps)), key))

    tl.append((slide_summary(temp_c, calc_out, weather_out), "summary"))
    tl.append((slide_outro(), "outro"))
    return tl


async def prepare_audio(keys_needed: List[str]) -> dict:
    import edge_tts
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    segs = {}
    for key in keys_needed:
        text = SCRIPTS[key]
        out = AUDIO_DIR / f"{key}.mp3"
        if not out.exists():
            print(f"[TTS] {key}...")
            await edge_tts.Communicate(text, VOICE).save(str(out))
        else:
            print(f"[TTS] reuse {key}")
        segs[key] = AudioSegment.from_mp3(str(out))
    return segs


def render(timeline, audio_segments):
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    clips = []
    full_audio = AudioSegment.silent(duration=0)
    for img, key in timeline:
        seg = audio_segments[key]
        clips.append((img, len(seg) + 300))
        full_audio += seg + AudioSegment.silent(duration=300)

    audio_out = AUDIO_DIR / "tokyo_full_audio.mp3"
    full_audio.export(str(audio_out), format="mp3")
    print(f"[OK] Audio {len(full_audio)/1000:.1f}s")

    concat_list = OUT_DIR / "tokyo_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for idx, (img, duration_ms) in enumerate(clips):
            path = FRAMES_DIR / f"scene_{idx:03d}.png"
            img.save(path, "PNG")
            rel = f"tokyo_frames/scene_{idx:03d}.png"
            f.write(f"file '{rel}'\n")
            f.write(f"duration {duration_ms/1000:.3f}\n")
            if idx % 5 == 0:
                print(f"  scene {idx+1}/{len(clips)}")
        f.write(f"file 'tokyo_frames/scene_{len(clips)-1:03d}.png'\n")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    raw = "tokyo_raw.mp4"
    print("[RENDER] Encoding...")
    r = subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", concat_list.name,
         "-vf", f"fps={FPS}", "-pix_fmt", "yuv420p", "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "23", raw],
        cwd=str(OUT_DIR), capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise RuntimeError("encode failed")

    print("[MUX] Adding audio...")
    r = subprocess.run(
        [ffmpeg, "-y", "-i", raw, "-i", str(Path("tokyo_audio") / audio_out.name),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", VIDEO_PATH.name],
        cwd=str(OUT_DIR), capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise RuntimeError("mux failed")

    try:
        (OUT_DIR / raw).unlink()
    except Exception:
        pass
    print(f"[DONE] {VIDEO_PATH}")
    return VIDEO_PATH


def main():
    print("=" * 60)
    print(" Tokyo Weather Agent — Full Educational Video")
    print("=" * 60)

    print("\n[1] Running live agent on Tokyo weather query...")
    agent = SimpleAgent(mode="simulated")
    steps = list(agent.run_step_by_step(QUERY))
    print(f"    Captured {len(steps)} steps")
    for s in steps:
        print(f"    - {s.step_type}: {s.title}")

    print("\n[2] Building slides (functional + technical + live)...")
    timeline = build_timeline(steps)
    keys = [k for _, k in timeline]
    print(f"    {len(timeline)} scenes")

    print("\n[3] Narration...")
    audio = asyncio.run(prepare_audio(keys))

    print("\n[4] Rendering MP4...")
    path = render(timeline, audio)
    mb = path.stat().st_size / (1024 * 1024)
    print()
    print("=" * 60)
    print(f" SUCCESS -> {path}")
    print(f" Size    -> {mb:.1f} MB")
    print("=" * 60)


if __name__ == "__main__":
    main()
