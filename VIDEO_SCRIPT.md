# 🎬 Video Script & Production Guide: "How AI Agents Work Step-by-Step"

This document provides a **complete, word-for-word teleprompter script and storyboard** designed for recording a YouTube video, tutorial, or LinkedIn demo.

---

## 📌 Video Overview
- **Title Options:**
  - *How AI Agents Actually Work (Step-by-Step Demo from Scratch)*
  - *Build & Understand an AI Agent in 5 Minutes (ReAct Framework)*
  - *Stop Using Chatbots: Build Your First AI Agent Step-by-Step*
- **Target Duration:** 4 to 6 minutes
- **Recommended Setup:**
  - Screen recording software (OBS Studio, Loom, or Screen Studio)
  - 1080p or 4K resolution
  - Open terminal with `python cli_demo.py` or browser with `streamlit run app.py`

---

## ⏱️ Video Timeline & Teleprompter Script

### 🕒 Scene 1: The Hook (0:00 - 0:45)
**Screen Setup:** Camera on you or showcasing the title banner in Terminal / Streamlit.

> **Voiceover:**
> *"Everyone is talking about AI Agents right now. But what actually is an AI Agent, and how does it differ from a regular ChatGPT conversation?*
>
> *A regular chatbot can only do one thing: you ask a question, it generates text, and stops. It cannot browse live data, it cannot verify mathematical computations, and it cannot take action in the real world.*
>
> *An AI Agent, on the other hand, is an LLM with **hands and eyes**. It uses a framework called **ReAct** — Reasoning plus Acting. It thinks, chooses tools, observes the results, and loops until the job is done.*
>
> *In this video, I will show you step-by-step how an AI Agent solves a real multi-step problem right in front of your eyes."*

---

### 🕒 Scene 2: The Core Framework (0:45 - 1:30)
**Screen Setup:** Show the 5-step visual diagram at the top of the Streamlit app (`streamlit run app.py`).

> **Voiceover:**
> *"Every single agent in the world follows this exact 5-step cycle:*
> 1. *First: **The Goal** — the user specifies what needs to be done.*
> 2. *Second: **The Thought** — the LLM's internal monologue breaks the problem into a plan.*
> 3. *Third: **The Action** — the agent selects an external tool (like a calculator or database) and prepares parameters.*
> 4. *Fourth: **The Observation** — the tool runs and returns factual data back to the agent.*
> 5. *Fifth: **The Final Answer** — once all steps are complete, the agent synthesizes everything into a verified response.*
>
> *Let's see this in action right now!"*

---

### 🕒 Scene 3: Live Demo — Step-by-Step Execution (1:30 - 3:30)
**Screen Setup:**
- Option A: Terminal (`python cli_demo.py` in interactive mode)
- Option B: Streamlit Web UI (`streamlit run app.py` using the **Next Step** button)

#### Step 1: User Goal
*(Click 'Next Step' or press [Enter])*
> **Voiceover:**
> *"Here is our goal: 'Calculate the total for an order of 50 units at $30 each, apply our VIP discount, and add 8% sales tax.'*
> *Notice that this is not a simple question. The model doesn't know what our company's VIP discount policy is, nor should it guess the final math."*

#### Step 2: Agent Thought & Tool Selection
*(Click 'Next Step' or press [Enter])*
> **Voiceover:**
> *"Look at Step 1: The agent pauses and reasons. It says: 'I need to calculate the total order price. First, let me check the VIP discount policy from the knowledge base.'*
> *Notice it does NOT guess the discount. It invokes the tool `search_knowledge_base` with parameter `vip_discount`."*

#### Step 3: Tool Observation
*(Click 'Next Step' or press [Enter])*
> **Voiceover:**
> *"In Step 3, the tool executes and returns: 'VIP Members receive a flat 20% discount on all purchases above $100.'*
> *The agent now observes this fact and stores it in its memory."*

#### Step 4: Next Thought & Precise Math Action
*(Click 'Next Step' or press [Enter])*
> **Voiceover:**
> *"Now the agent enters cycle number two. It reasons: '50 units times $30 is $1,500. A 20% discount brings it to $1,200. Plus 8% sales tax.'*
> *LLMs are notorious for hallucinating math. But our agent doesn't do the math inside its neural network weights — it delegates the exact expression `(50 * 30 * 0.80) * 1.08` to our safe calculator tool!"*

#### Step 5: Final Observation & Verified Answer
*(Click 'Next Step' or press [Enter])*
> **Voiceover:**
> *"The calculator returns `1296.0`.*
> *And in Step 7, the agent delivers the final synthesized answer:*
> *- Base Price: $1,500*
> *- VIP Discount: -$300*
> *- Tax: +$96*
> *- Final Verified Total: $1,296.00.*
> *Zero hallucinations, 100% grounded in real tools and policy documents."*

---

### 🕒 Scene 4: Quick Code Walkthrough (3:30 - 4:45)
**Screen Setup:** Open `agent.py` and `tools.py` in the IDE.

> **Voiceover:**
> *"Building this is surprisingly simple. Let me show you the code.*
> *In `tools.py`, each tool is just a clean Python function. We have a calculator and a database lookup.*
> *In `agent.py`, the core loop is just a Python generator or `while` loop that iterates until the LLM decides no more tools are required.*
> *You can run this in two modes:*
> *1. **Simulator Mode**: zero API keys required, perfect for fast offline demos.*
> *2. **Live OpenAI Mode**: where GPT-4o-mini dynamically decides tool calls in real-time."*

---

### 🕒 Scene 5: Outro & Call to Action (4:45 - 5:15)
**Screen Setup:** Back on camera or showing repository links.

> **Voiceover:**
> *"And that's how an AI Agent works from the inside out!*
> *All the code for this step-by-step project, including the CLI and Streamlit visualizer, is available in the description below.*
> *If you found this helpful, hit that Like button, subscribe for more practical AI engineering tutorials, and let me know in the comments what agent you want to build next! Thanks for watching!"*
