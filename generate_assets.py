"""
generate_assets.py - Auto-create PowerPoint slides + AI voiceover audio for the video.
Run once:  python generate_assets.py
"""

import asyncio
import os
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
SLIDES_DIR = ROOT / "video_assets"
AUDIO_DIR = SLIDES_DIR / "audio"
PPTX_PATH = SLIDES_DIR / "AI_Agent_Step_By_Step.pptx"

# ---------------------------------------------------------------------------
# Voiceover scripts (spoken narration for each scene)
# ---------------------------------------------------------------------------
VOICEOVERS = {
    "01_hook": (
        "Everyone is talking about AI Agents right now. But what actually is an AI Agent, "
        "and how does it differ from a regular ChatGPT conversation? "
        "A regular chatbot can only do one thing: you ask a question, it generates text, and stops. "
        "It cannot browse live data, it cannot verify mathematical computations, and it cannot take action "
        "in the real world. An AI Agent, on the other hand, is an LLM with hands and eyes. "
        "It uses a framework called ReAct — Reasoning plus Acting. It thinks, chooses tools, "
        "observes the results, and loops until the job is done. "
        "In this video, I will show you step-by-step how an AI Agent solves a real multi-step problem "
        "right in front of your eyes."
    ),
    "02_framework": (
        "Every single agent in the world follows this exact five-step cycle. "
        "First: The Goal — the user specifies what needs to be done. "
        "Second: The Thought — the LLM's internal monologue breaks the problem into a plan. "
        "Third: The Action — the agent selects an external tool like a calculator or database, "
        "and prepares parameters. "
        "Fourth: The Observation — the tool runs and returns factual data back to the agent. "
        "Fifth: The Final Answer — once all steps are complete, the agent synthesizes everything "
        "into a verified response. Let's see this in action right now!"
    ),
    "03_goal": (
        "Here is our goal: Calculate the total for an order of 50 units at 30 dollars each, "
        "apply our VIP discount, and add 8 percent sales tax. "
        "Notice that this is not a simple question. The model doesn't know what our company's "
        "VIP discount policy is, nor should it guess the final math."
    ),
    "04_thought_action": (
        "Look at Step 1: The agent pauses and reasons. It says: I need to calculate the total "
        "order price. First, let me check the VIP discount policy from the knowledge base. "
        "Notice it does NOT guess the discount. It invokes the tool search knowledge base "
        "with parameter vip underscore discount."
    ),
    "05_observation": (
        "In Step 3, the tool executes and returns: VIP Members receive a flat 20 percent discount "
        "on all purchases above 100 dollars. The agent now observes this fact and stores it in its memory."
    ),
    "06_math_action": (
        "Now the agent enters cycle number two. It reasons: 50 units times 30 dollars is 1,500 dollars. "
        "A 20 percent discount brings it to 1,200. Plus 8 percent sales tax. "
        "LLMs are notorious for hallucinating math. But our agent doesn't do the math inside its "
        "neural network weights — it delegates the exact expression to our safe calculator tool!"
    ),
    "07_final_answer": (
        "The calculator returns 1,296. And in the final step, the agent delivers the verified answer: "
        "Base price 1,500 dollars. VIP discount minus 300. Tax plus 96. "
        "Final verified total: 1,296 dollars. Zero hallucinations, 100 percent grounded in real tools "
        "and policy documents."
    ),
    "08_code_outro": (
        "Building this is surprisingly simple. In tools.py, each tool is just a clean Python function. "
        "In agent.py, the core loop iterates until the LLM decides no more tools are required. "
        "You can run this in Simulator Mode with zero API keys, or Live OpenAI Mode with GPT-4o-mini. "
        "And that's how an AI Agent works from the inside out! "
        "If you found this helpful, hit Like, subscribe, and tell me what agent you want to build next. "
        "Thanks for watching!"
    ),
}

# ---------------------------------------------------------------------------
# PowerPoint helpers
# ---------------------------------------------------------------------------
DARK = RGBColor(0x0F, 0x17, 0x2A)      # near-black navy
ACCENT = RGBColor(0x0E, 0xA5, 0xE9)    # sky blue
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x94, 0xA3, 0xB8)
GREEN = RGBColor(0x10, 0xB9, 0x81)
PURPLE = RGBColor(0x8B, 0x5C, 0xF6)
AMBER = RGBColor(0xF5, 0x9E, 0x0B)


def set_run(run, text, size=28, bold=False, color=WHITE, font="Calibri"):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_bg(slide, color=DARK):
    fill = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    fill.fill.solid()
    fill.fill.fore_color.rgb = color
    fill.line.fill.background()
    # Send to back
    spTree = slide.shapes._spTree
    sp = fill._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def add_title_block(slide, title, subtitle=None, y=2.2):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(y), Inches(11.7), Inches(1.4))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run() if False else p.runs[0] if p.runs else None, "", size=40)
    # Clear and rewrite cleanly
    tf.clear()
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    set_run(run, title, size=40, bold=True, color=WHITE)

    if subtitle:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        run2 = p2.add_run()
        set_run(run2, subtitle, size=20, bold=False, color=MUTED)


def add_bullet_slide(prs, title, bullets, accent_note=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    add_bg(slide)

    # Accent bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.15), Inches(7.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()

    # Title
    tbox = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12), Inches(0.9))
    tf = tbox.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    set_run(run, title, size=32, bold=True, color=WHITE)

    # Bullets
    bbox = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.5), Inches(5.2))
    tf = bbox.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(14)
        run = p.add_run()
        set_run(run, f"  {bullet}", size=22, color=WHITE)

    if accent_note:
        nbox = slide.shapes.add_textbox(Inches(0.8), Inches(6.7), Inches(11.5), Inches(0.5))
        tf = nbox.text_frame
        p = tf.paragraphs[0]
        run = p.add_run()
        set_run(run, accent_note, size=16, color=ACCENT)

    return slide


def add_title_slide(prs, title, subtitle, badge=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)

    # Top accent strip
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    strip.fill.solid()
    strip.fill.fore_color.rgb = ACCENT
    strip.line.fill.background()

    if badge:
        b = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(0.5))
        tf = b.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        set_run(run, badge, size=16, bold=True, color=ACCENT)

    tbox = slide.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(11.7), Inches(1.6))
    tf = tbox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    set_run(run, title, size=44, bold=True, color=WHITE)

    sbox = slide.shapes.add_textbox(Inches(1.5), Inches(4.3), Inches(10.3), Inches(1.0))
    tf = sbox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    set_run(run, subtitle, size=20, color=MUTED)

    return slide


def add_flow_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)

    tbox = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12), Inches(0.8))
    tf = tbox.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    set_run(run, "The ReAct Loop — 5 Steps", size=32, bold=True, color=WHITE)

    steps = [
        ("1. Goal", "User intent", ACCENT),
        ("2. Thought", "LLM plans", RGBColor(0x06, 0xB6, 0xD4)),
        ("3. Action", "Call a tool", PURPLE),
        ("4. Observe", "Read result", GREEN),
        ("5. Answer", "Final output", AMBER),
    ]

    box_w = Inches(2.1)
    box_h = Inches(1.8)
    start_x = Inches(0.7)
    y = Inches(2.8)
    gap = Inches(0.35)

    for i, (label, desc, color) in enumerate(steps):
        x = start_x + i * (box_w + gap)
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, box_w, box_h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.fill.background()

        tf = shape.text_frame
        tf.word_wrap = True
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        run = tf.paragraphs[0].add_run()
        set_run(run, label, size=18, bold=True, color=WHITE)
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        run2 = p2.add_run()
        set_run(run2, desc, size=14, color=WHITE)

        if i < len(steps) - 1:
            arrow = slide.shapes.add_textbox(
                x + box_w - Inches(0.05), y + Inches(0.65), Inches(0.4), Inches(0.4)
            )
            # Use a simple ">" as arrow between boxes
            pass

    note = slide.shapes.add_textbox(Inches(0.7), Inches(5.5), Inches(12), Inches(1.2))
    tf = note.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    set_run(
        run,
        "Thought → Action → Observation repeats until the goal is fully solved.",
        size=18,
        color=MUTED,
    )
    return slide


def create_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    add_title_slide(
        prs,
        "How AI Agents Actually Work",
        "A step-by-step demonstration of the ReAct framework\n(Reasoning + Acting + Tools)",
        badge="VIDEO TUTORIAL  ·  5 MINUTES",
    )

    add_bullet_slide(
        prs,
        "Chatbot  vs  AI Agent",
        [
            "Chatbot: Prompt → Text → Stop",
            "Cannot call APIs, databases, or calculators",
            "Often hallucinates math and policies",
            "",
            "AI Agent: Reason → Act → Observe → Loop",
            "Uses tools as hands and eyes",
            "Verified answers grounded in real data",
        ],
        accent_note="Key idea: Agents don't just talk — they take action.",
    )

    add_flow_slide(prs)

    add_bullet_slide(
        prs,
        "Demo Goal",
        [
            '"Calculate the total for 50 units at $30 each,',
            ' apply the VIP discount, and add 8% sales tax."',
            "",
            "Why this is a great agent demo:",
            "• Needs a knowledge-base lookup (VIP policy)",
            "• Needs accurate math (no LLM guessing)",
            "• Multi-step reasoning before final answer",
        ],
    )

    add_bullet_slide(
        prs,
        "Step 1–3: Thought → Tool → Observation",
        [
            "Thought: \"I don't know the VIP discount — look it up.\"",
            "Action: search_knowledge_base(query=\"vip_discount\")",
            "Observation: \"VIP members get 20% off orders over $100.\"",
            "",
            "The agent stores this fact in memory before continuing.",
        ],
        accent_note="No guessing. Policy comes from a real tool.",
    )

    add_bullet_slide(
        prs,
        "Step 4–6: Math Cycle (No Hallucinations)",
        [
            "Thought: 50 × $30 = $1,500 → 20% off → + 8% tax",
            "Action: calculator(\"(50 * 30 * 0.80) * 1.08\")",
            "Observation: 1296.0",
            "",
            "Final Answer: $1,296.00",
            "  Base $1,500  −  Discount $300  +  Tax $96",
        ],
        accent_note="LLMs don't do math — tools do.",
    )

    add_bullet_slide(
        prs,
        "Project Files (What You Just Built)",
        [
            "agent.py   → ReAct loop (Thought / Action / Observation)",
            "tools.py   → calculator, weather, knowledge base",
            "cli_demo.py → Terminal step-by-step for video recording",
            "app.py     → Streamlit visual dashboard",
            "VIDEO_SCRIPT.md → Full teleprompter narration",
        ],
        accent_note="Simulator mode works offline with zero API keys.",
    )

    add_title_slide(
        prs,
        "That's How an AI Agent Works",
        "Like · Subscribe · Comment what agent you want to build next",
        badge="THANKS FOR WATCHING",
    )

    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    prs.save(str(PPTX_PATH))
    print(f"[OK] PowerPoint saved -> {PPTX_PATH}")


# ---------------------------------------------------------------------------
# Edge-TTS voiceover generation
# ---------------------------------------------------------------------------
async def generate_one(name: str, text: str, voice: str = "en-US-JennyNeural"):
    import edge_tts

    out = AUDIO_DIR / f"{name}.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out))
    print(f"[OK] Audio -> {out.name}")


async def generate_all_audio():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    tasks = [generate_one(name, text) for name, text in VOICEOVERS.items()]
    await asyncio.gather(*tasks)

    # Also stitch a single combined narration file if pydub is available
    try:
        from pydub import AudioSegment

        combined = AudioSegment.silent(duration=500)
        for name in VOICEOVERS.keys():
            path = AUDIO_DIR / f"{name}.mp3"
            if path.exists():
                combined += AudioSegment.from_mp3(str(path))
                combined += AudioSegment.silent(duration=800)
        out = AUDIO_DIR / "00_FULL_NARRATION.mp3"
        combined.export(str(out), format="mp3")
        print(f"[OK] Combined narration -> {out}")
    except Exception as e:
        print(f"[INFO] Combined MP3 skipped ({e}). Individual scene files are ready.")


def main():
    print("=" * 60)
    print(" Creating video assets: PowerPoint + AI Voiceover")
    print("=" * 60)
    create_pptx()
    print()
    print("Generating AI voiceovers with edge-tts (JennyNeural)...")
    asyncio.run(generate_all_audio())
    print()
    print("=" * 60)
    print(" DONE - Open folder: video_assets/")
    print(f"  Slides : {PPTX_PATH.name}")
    print(f"  Audio  : video_assets/audio/*.mp3")
    print("=" * 60)


if __name__ == "__main__":
    main()
