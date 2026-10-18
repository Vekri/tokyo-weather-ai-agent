# Tokyo Weather AI Agent

Simple **ReAct AI Agent** in Python — fetch Tokyo weather, convert °C → °F, and show every step:
**Goal → Thought → Action → Observation → Final Answer**.

Built for tutorials, demos, and YouTube walkthroughs.

---

## YouTube

- Full titles, story, description, timestamps, tags → [`YOUTUBE.md`](YOUTUBE.md)
- Teleprompter script → [`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md)
- Generate Tokyo demo MP4 → `python create_tokyo_video.py`

---

## Python paths (GitHub layout)

```text
.
├── tools.py                 # CREATE TOOLS — get_weather, calculator, knowledge base
├── agent.py                 # CREATE AGENT — SimpleAgent ReAct loop
├── config.py                # Settings / env
├── cli_demo.py              # Terminal step-by-step demo
├── app.py                   # Streamlit web demo
├── create_tokyo_video.py    # Tokyo weather educational video (MP4)
├── create_video.py          # Full multi-scenario video
├── generate_assets.py       # PPT + voiceover assets
├── requirements.txt
├── YOUTUBE.md               # YouTube title / description / story
└── VIDEO_SCRIPT.md
```

---

## Quick start

```bash
git clone https://github.com/Vekri/tokyo-weather-ai-agent.git
cd tokyo-weather-ai-agent
pip install -r requirements.txt
```

### 1) Terminal demo (best for screen recording)

```bash
python cli_demo.py
# auto-play:
python cli_demo.py --auto --delay 2.0
```

### 2) Web demo

```bash
streamlit run app.py
```

### 3) Minimal code — Tokyo weather agent

```python
from agent import SimpleAgent

query = "Check the current weather in Tokyo and convert the temperature to Fahrenheit."
agent = SimpleAgent(mode="simulated")

for step in agent.run_step_by_step(query):
    print(f"[{step.step_type}] {step.title}")
    print(step.content)
    print("Description:", step.explanation)
    print("-" * 40)
```

### 4) Generate the YouTube video (MP4)

```bash
python create_tokyo_video.py
# Output: video_assets/Tokyo_Weather_Agent_Demo.mp4
```

---

## How the agent is created (technical)

| Piece | File | Responsibility |
|-------|------|----------------|
| Tools | `tools.py` | `get_weather()`, `calculator()`, `TOOL_REGISTRY` |
| Agent | `agent.py` | `SimpleAgent` yields ReAct steps |
| Demo UI | `cli_demo.py`, `app.py` | Show each step live |

**Functional flow (Tokyo):**
1. User asks for Tokyo weather + Fahrenheit  
2. Agent thinks → calls `get_weather("Tokyo")`  
3. Observes °C → calls `calculator("(C * 9/5) + 32")`  
4. Returns verified weather report  

Simulator mode works **offline** (no API key). Optional live OpenAI mode via `.env` (`OPENAI_API_KEY`).

---

## License

MIT — use freely for learning, tutorials, and demos.
