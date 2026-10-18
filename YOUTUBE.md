# YouTube Pack — Tokyo Weather AI Agent

Copy-paste ready: **titles**, **story**, **description**, **tags**, **timestamps**, and **GitHub code paths**.

---

## 1) Video Titles (pick one)

1. **How an AI Agent Works: Tokyo Weather Demo (ReAct Explained Step-by-Step)**
2. **Build a Tokyo Weather AI Agent in Python — Functional + Technical Walkthrough**
3. **Stop Using Chatbots — Build a Real AI Agent (Weather + Calculator Tools)**
4. **AI Agent from Scratch: Goal → Thought → Action → Observation → Answer**

**Recommended:** Title #1

**Thumbnail text ideas:** `AI AGENT` · `TOKYO WEATHER` · `REACT LOOP`

---

## 2) YouTube Story (spoken narrative / storyboard)

### Hook (0:00)
Everyone talks about AI Agents. But what actually happens when an agent answers:
“What’s the weather in Tokyo in Fahrenheit?”
A chatbot might guess. An agent uses tools.

### Functional story (0:20)
The user wants two things in one sentence:
1. Current weather in Tokyo
2. Temperature converted to Fahrenheit

The agent’s job is not to invent numbers — it must fetch weather, calculate conversion, then report clearly.

### Technical story (0:50)
We create the agent in two Python files:

| File | Role |
|------|------|
| `tools.py` | Hands of the agent — `get_weather()`, `calculator()` |
| `agent.py` | Brain of the agent — ReAct loop (Thought → Action → Observe) |

### How it works (1:20)
ReAct cycle for Tokyo:
1. **GOAL** — receive the query  
2. **THOUGHT** — “I need live weather for Tokyo”  
3. **ACTION** — `get_weather(city="Tokyo")`  
4. **OBSERVATION** — e.g. 18°C, Partly Cloudy  
5. **THOUGHT** — “Convert with (C × 9/5) + 32”  
6. **ACTION** — `calculator("(18 * 9 / 5) + 32")`  
7. **OBSERVATION** — 64.4°F  
8. **FINAL ANSWER** — full weather report  

### Live proof (2:00)
We run `SimpleAgent().run_step_by_step(query)` and show every real step + tool output.

### Closing (end)
That’s how you create an AI Agent and how it works: tools + ReAct loop + verified answers.

---

## 3) YouTube Description (copy below)

```text
🤖 How an AI Agent Works — Tokyo Weather Demo (ReAct Step-by-Step)

In this video we build and run a simple AI Agent in Python that answers:
"Check the current weather in Tokyo and convert the temperature to Fahrenheit."

You will learn BOTH:
✅ FUNCTIONAL — what the agent does for the user
✅ TECHNICAL — how the agent is created and how the ReAct loop works

🔥 What you’ll see
• Chatbot vs AI Agent
• Creating tools in tools.py (get_weather + calculator)
• Creating the agent in agent.py (SimpleAgent ReAct loop)
• Live tool execution with real outputs
• Full step-by-step run: Goal → Thought → Action → Observation → Final Answer

📦 GitHub / Source Code
👉 https://github.com/Vekri/tokyo-weather-ai-agent

📁 Important Python paths in the repo
• tools.py                 → Agent tools (weather + calculator)
• agent.py                 → SimpleAgent ReAct engine
• cli_demo.py              → Terminal step-by-step demo
• app.py                   → Streamlit visual demo
• create_tokyo_video.py    → Generate this tutorial video (MP4)
• requirements.txt         → Dependencies

▶️ Quick start
```bash
git clone https://github.com/Vekri/tokyo-weather-ai-agent.git
cd tokyo-weather-ai-agent
pip install -r requirements.txt
python cli_demo.py
# or
streamlit run app.py
# generate the Tokyo video
python create_tokyo_video.py
```

⏱️ Timestamps
0:00 Intro — Why AI Agents (not just chatbots)
0:20 Functional view — User goal & outcome
0:50 Technical architecture — tools.py + agent.py
1:20 How tools are created
1:50 How the agent ReAct loop is created
2:20 ReAct explained for Tokyo weather
2:50 Live tool call: get_weather("Tokyo")
3:20 Live tool call: calculator (C → F)
3:50 Full live agent run (all 8 steps)
4:20 Results + technical takeaways
4:40 Outro

🏷️ Keywords
AI Agent, ReAct Framework, Python AI Agent, LangChain alternative, Tool Calling, OpenAI Agents, Weather Agent, AI Tutorial, Agentic AI, Function Calling

👍 Like + Subscribe if you want Part 2 (multi-agent / live OpenAI API version)

#AIAgent #Python #ReAct #GenerativeAI #AITutorial #MachineLearning #OpenAI #AgenticAI
```

> GitHub: https://github.com/Vekri/tokyo-weather-ai-agent

---

## 4) Tags (YouTube)

```
AI Agent, ReAct, Python AI, tool calling, weather agent, OpenAI, agentic AI, AI tutorial, chatbot vs agent, function calling, Streamlit, SimpleAgent
```

---

## 5) Pinned Comment (optional)

```text
🔗 Full source code on GitHub:
https://github.com/Vekri/tokyo-weather-ai-agent

Start here:
1) tools.py — create tools
2) agent.py — create ReAct agent
3) python cli_demo.py — watch steps live

Comment “TOKYO” if you want the live OpenAI API version next!
```

---

## 6) GitHub Python Path Map

```
tokyo-weather-ai-agent/          ← GitHub repo root
│
├── README.md                    ← Project docs
├── YOUTUBE.md                   ← This YouTube pack
├── VIDEO_SCRIPT.md              ← Full teleprompter script
├── requirements.txt             ← pip dependencies
├── .env.example                 ← Optional OPENAI_API_KEY
├── .gitignore
│
├── tools.py                     ← CREATE TOOLS (get_weather, calculator, ...)
├── agent.py                     ← CREATE AGENT (SimpleAgent ReAct loop)
├── config.py                    ← Settings
│
├── cli_demo.py                  ← Run: python cli_demo.py
├── app.py                       ← Run: streamlit run app.py
│
├── create_tokyo_video.py        ← Run: python create_tokyo_video.py
├── create_video.py              ← Full multi-scenario video
└── generate_assets.py           ← PPT + voiceover assets
```

### Core code entry points

| Path | Command / Purpose |
|------|-------------------|
| `tools.py` | Tool functions used by the agent |
| `agent.py` | `SimpleAgent().run_step_by_step(query)` |
| `cli_demo.py` | `python cli_demo.py` — interactive terminal demo |
| `app.py` | `streamlit run app.py` — web demo |
| `create_tokyo_video.py` | `python create_tokyo_video.py` → MP4 |

### Minimal demo snippet (for description / comments)

```python
from agent import SimpleAgent

query = "Check the current weather in Tokyo and convert the temperature to Fahrenheit."
agent = SimpleAgent(mode="simulated")

for step in agent.run_step_by_step(query):
    print(step.step_type, "=>", step.title)
    print(step.content)
    print("---")
```
