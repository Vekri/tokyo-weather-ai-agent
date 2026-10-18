"""
config.py - Configuration settings for the AI Agent demo.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI or compatible LLM settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

# Presentation settings
DEFAULT_DELAY = float(os.getenv("STEP_DELAY", "1.5"))
DEFAULT_MODE = os.getenv("AGENT_MODE", "simulated")  # "simulated" or "openai"
