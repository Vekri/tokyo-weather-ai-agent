"""
app.py - Streamlit Interactive Web Application for Video Demonstrations.

Run with:
    streamlit run app.py
"""

import time
import json
import streamlit as st
from agent import SimpleAgent, AgentStep
from tools import TOOL_DESCRIPTIONS, OPENAI_TOOLS

# Configure page
st.set_page_config(
    page_title="AI Agent Step-by-Step Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for presentation-grade aesthetics
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .flow-badge {
        display: inline-block;
        padding: 6px 12px;
        margin: 4px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .step-card {
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 6px solid #3B82F6;
        background-color: #F8FAFC;
    }
    .thought-card {
        border-left-color: #06B6D4 !important;
        background-color: #F0FDFA;
    }
    .action-card {
        border-left-color: #8B5CF6 !important;
        background-color: #F5F3FF;
    }
    .observation-card {
        border-left-color: #10B981 !important;
        background-color: #ECFDF5;
    }
    .final-card {
        border-left-color: #F59E0B !important;
        background-color: #FFFBEB;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
st.sidebar.title("🛠️ Agent Configuration")

mode = st.sidebar.radio(
    "Execution Engine:",
    ["Simulator Mode (Zero-Setup / Ideal for Video)", "Live OpenAI API"],
    index=0,
    help="Simulator mode works 100% offline without API keys. Live mode calls OpenAI."
)

api_key = None
if mode == "Live OpenAI API":
    api_key = st.sidebar.text_input("OpenAI API Key:", type="password", placeholder="sk-...")
    if not api_key:
        st.sidebar.warning("Please enter your OpenAI API key to use live mode.")

st.sidebar.divider()
st.sidebar.subheader("🎬 Video Scenarios")

preset_options = {
    "Financial Analyst (Discount & Tax)": (
        "Calculate the total for an order of 50 units at $30 each, apply the VIP discount, and add 8% sales tax."
    ),
    "Travel Assistant (Tokyo Weather)": (
        "Check the current weather in Tokyo and convert the temperature to Fahrenheit."
    ),
    "Customer Support (Return & Restocking)": (
        "A customer wants to return a $200 item purchased 45 days ago. Check the policy and calculate the refund."
    ),
    "Custom Goal": ""
}

selected_scenario = st.sidebar.selectbox("Choose Demo Scenario:", list(preset_options.keys()))

if selected_scenario == "Custom Goal":
    user_query = st.sidebar.text_area("Custom User Goal:", value="Calculate 125 * 48 with 12% discount")
else:
    user_query = preset_options[selected_scenario]

st.sidebar.divider()
animation_delay = st.sidebar.slider("Narration Pause (seconds per step):", 0.0, 3.0, 1.2, 0.2)

# -----------------------------------------------------------------------------
# Main Header
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">🤖 How an AI Agent Works: Step-by-Step</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Visualizing the <b>ReAct</b> (Reasoning + Acting) cycle in action. Perfect for tutorial videos and demonstrations.</div>', unsafe_allow_html=True)

# Visual Pipeline Diagram
col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
with col_p1:
    st.info("🎯 **1. Goal**\nUser intent")
with col_p2:
    st.info("🧠 **2. Thought**\nLLM Plan")
with col_p3:
    st.info("🛠️ **3. Action**\nTool Call")
with col_p4:
    st.info("👁️ **4. Observe**\nTool Output")
with col_p5:
    st.success("✅ **5. Answer**\nFinal Result")

st.divider()

# -----------------------------------------------------------------------------
# Session State for Step-by-Step Stepping
# -----------------------------------------------------------------------------
if "steps" not in st.session_state:
    st.session_state.steps = []
if "current_step_idx" not in st.session_state:
    st.session_state.current_step_idx = 0
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# Control buttons
col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 3])

with col_btn1:
    run_all = st.button("▶️ Auto-Run Full Demo", type="primary", use_container_width=True)
with col_btn2:
    step_forward = st.button("⏭️ Next Step (Manual Voiceover)", use_container_width=True)
with col_btn3:
    reset_btn = st.button("🔄 Reset", use_container_width=False)

if reset_btn:
    st.session_state.steps = []
    st.session_state.current_step_idx = 0
    st.rerun()

# Initialize or re-fetch steps if query changes
agent_mode = "openai" if ("Live OpenAI" in mode and api_key) else "simulated"
agent = SimpleAgent(mode=agent_mode, api_key=api_key)

if run_all or not st.session_state.steps:
    st.session_state.steps = list(agent.run_step_by_step(user_query))
    if run_all:
        st.session_state.current_step_idx = len(st.session_state.steps)
    elif not st.session_state.steps:
        st.session_state.current_step_idx = 1

if step_forward:
    if st.session_state.current_step_idx < len(st.session_state.steps):
        st.session_state.current_step_idx += 1
    st.rerun()

# -----------------------------------------------------------------------------
# Render Visible Steps
# -----------------------------------------------------------------------------
visible_steps = st.session_state.steps[:st.session_state.current_step_idx]
total_steps = len(st.session_state.steps)

# Progress indicator
progress_val = min(1.0, (st.session_state.current_step_idx / max(1, total_steps)))
st.progress(progress_val, text=f"Step {st.session_state.current_step_idx} of {total_steps}")

for step in visible_steps:
    step_type = step.step_type

    if step_type == "GOAL":
        with st.container():
            st.markdown(f"""
            <div class="step-card">
                <h4>{step.title}</h4>
                <p style="font-size: 1.15rem; font-weight: 600; color: #1E293B;">"{step.content}"</p>
                <small style="color: #64748B;">ℹ️ <b>Concept:</b> {step.explanation}</small>
            </div>
            """, unsafe_allow_html=True)

    elif step_type == "THOUGHT":
        with st.container():
            st.markdown(f"""
            <div class="step-card thought-card">
                <h4>{step.title}</h4>
                <p style="font-size: 1.05rem; color: #0F766E;">{step.content}</p>
                <small style="color: #0D9488;">ℹ️ <b>Concept:</b> {step.explanation}</small>
            </div>
            """, unsafe_allow_html=True)

    elif step_type == "ACTION":
        with st.container():
            st.markdown(f"""
            <div class="step-card action-card">
                <h4>{step.title}</h4>
                <p><b>Tool:</b> <code>{step.tool_name}</code></p>
            </div>
            """, unsafe_allow_html=True)
            if step.tool_args:
                with st.expander("🔍 View Tool Arguments (JSON Payload)", expanded=True):
                    st.json(step.tool_args)

    elif step_type == "OBSERVATION":
        with st.container():
            st.markdown(f"""
            <div class="step-card observation-card">
                <h4>{step.title}</h4>
                <p style="font-size: 1.05rem; font-family: monospace; color: #065F46;">{step.content}</p>
                <small style="color: #059669;">ℹ️ <b>Concept:</b> {step.explanation}</small>
            </div>
            """, unsafe_allow_html=True)

    elif step_type == "FINAL_ANSWER":
        with st.container():
            st.markdown(f"""
            <div class="step-card final-card">
                <h3>{step.title}</h3>
            </div>
            """, unsafe_allow_html=True)
            st.success("Task completed successfully!")
            st.markdown(step.content)

# -----------------------------------------------------------------------------
# Educational Expanders for Presenter / Video Screen Recording
# -----------------------------------------------------------------------------
st.divider()

tab1, tab2, tab3 = st.tabs(["📚 Core Agent Architecture", "🛠️ Tool Registry & Schemas", "🎙️ Ready Video Script"])

with tab1:
    st.markdown("""
    ### Why are AI Agents different from standard Chatbots?
    
    1. **Standard Chatbot (Single Turn):**
       - Prompt ➡️ LLM ➡️ Answer
       - Cannot browse real-time data, cannot run accurate multi-step math, cannot take action in the real world.
    
    2. **AI Agent (ReAct Loop):**
       - **Reason (Thought):** Decides *what* it needs to accomplish next.
       - **Act (Action):** Calls external APIs, databases, or calculators.
       - **Observe (Observation):** Inspects the tool output and updates memory.
       - **Iterate:** Continues until the goal is fully achieved.
    """)

with tab2:
    st.markdown("### The Tools Available to this Agent:")
    st.code(TOOL_DESCRIPTIONS, language="markdown")
    with st.expander("View OpenAI Function Calling Schemas"):
        st.json(OPENAI_TOOLS)

with tab3:
    st.markdown("""
    ### 🎙️ 2-Minute Video Narration Outline:
    
    - **0:00 - Hook:** "Everyone talks about AI Agents, but what actually happens under the hood? In this video, I'll break down the ReAct loop step-by-step."
    - **0:30 - The Goal:** "Notice we give our agent a multi-part question: checking a discount policy, calculating prices, and applying taxes."
    - **1:00 - The ReAct Loop:** "Watch Step 1: The agent *thinks* first. It realizes it doesn't know the discount, so it selects the knowledge base tool."
    - **1:30 - Tool Calling:** "Next, it receives the tool observation, thinks again, and calls the calculator. Notice it never guesses or hallucinates the math!"
    - **2:00 - Final Synthesis:** "Finally, it delivers the verified answer. That's all an AI Agent is: an LLM with reasoning, memory, and tools!"
    """)
