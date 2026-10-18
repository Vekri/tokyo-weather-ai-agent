# Tokyo Weather AI Agent

Simple **ReAct AI Agent** in Python — fetch Tokyo weather, convert °C → °F, and show every step:
**Goal → Thought → Action → Observation → Final Answer**.

---

## Project layout

```text
.
├── tools.py               # CREATE TOOLS — get_weather, calculator, knowledge base
├── agent.py               # CREATE AGENT — SimpleAgent ReAct loop
├── config.py              # Settings / env
├── cli_demo.py            # Terminal step-by-step demo
├── app.py                 # Streamlit web demo
├── examples/tokyo_run.py  # Minimal Tokyo weather run script
├── requirements.txt
└── .env.example
```

---

## Quick start

```bash
git clone https://github.com/Vekri/tokyo-weather-ai-agent.git
cd tokyo-weather-ai-agent
pip install -r requirements.txt
```

### Terminal demo

```bash
python cli_demo.py
# auto-play:
python cli_demo.py --auto --delay 2.0
```

### Web demo

```bash
streamlit run app.py
```

### Minimal Tokyo weather run

```bash
python examples/tokyo_run.py
```

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

---

## How the agent works

| Piece | File | Responsibility |
|-------|------|----------------|
| Tools | `tools.py` | `get_weather()`, `calculator()`, `TOOL_REGISTRY` |
| Agent | `agent.py` | `SimpleAgent` yields ReAct steps |
| Demo UI | `cli_demo.py`, `app.py` | Show each step live |

**Tokyo flow:**
1. User asks for Tokyo weather + Fahrenheit  
2. Agent thinks → calls `get_weather("Tokyo")`  
3. Observes °C → calls `calculator("(C * 9/5) + 32")`  
4. Returns verified weather report  

Simulator mode works **offline** (no API key). Optional live OpenAI mode via `.env` (`OPENAI_API_KEY`).

---

## License

MIT — use freely for learning, tutorials, and demos.
