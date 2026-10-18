"""
tools.py - Simple, safe, and modular tools for our AI Agent.
Tools represent the "hands and eyes" of an AI agent, allowing it to interact
with external systems, perform calculations, and fetch data.
"""

import ast
import operator
import json
from typing import Dict, Any, Callable

# -----------------------------------------------------------------------------
# 1. Safe Calculator Tool
# -----------------------------------------------------------------------------
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}

def _eval_expr(node):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_expr(node.left)
        right = _eval_expr(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_expr(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")
    else:
        raise TypeError(f"Unsupported expression element: {type(node)}")

def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely.
    Example: calculator('1500 * 45 * 1.08')
    """
    clean_expr = expression.strip().replace(",", "")
    try:
        parsed = ast.parse(clean_expr, mode='eval')
        result = _eval_expr(parsed.body)
        # Format cleanly
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression '{expression}': {str(e)}"

# -----------------------------------------------------------------------------
# 2. Weather Tool (Simulated Live Data)
# -----------------------------------------------------------------------------
WEATHER_DATABASE = {
    "tokyo": {"temperature_c": 18, "condition": "Partly Cloudy", "humidity": "62%"},
    "new york": {"temperature_c": 22, "condition": "Sunny", "humidity": "45%"},
    "london": {"temperature_c": 14, "condition": "Light Rain", "humidity": "80%"},
    "paris": {"temperature_c": 16, "condition": "Breezy", "humidity": "58%"},
    "san francisco": {"temperature_c": 19, "condition": "Foggy morning, clear afternoon", "humidity": "68%"},
    "sydney": {"temperature_c": 24, "condition": "Sunny", "humidity": "50%"},
    "mumbai": {"temperature_c": 31, "condition": "Humid and Warm", "humidity": "75%"},
    "hyderabad": {"temperature_c": 29, "condition": "Clear Sky", "humidity": "55%"},
    "bengaluru": {"temperature_c": 26, "condition": "Pleasant and Breezy", "humidity": "60%"}
}

def get_weather(city: str) -> str:
    """Get the current weather forecast for a given city.
    Example: get_weather('Tokyo')
    """
    city_key = city.strip().lower()
    if city_key in WEATHER_DATABASE:
        info = WEATHER_DATABASE[city_key]
        return (
            f"Weather in {city.title()}: {info['temperature_c']}°C, "
            f"{info['condition']}, Humidity: {info['humidity']}."
        )
    return f"Weather in {city.title()}: 21°C, Mild and Clear (Standard forecast)."

# -----------------------------------------------------------------------------
# 3. Knowledge Base / Database Lookup Tool
# -----------------------------------------------------------------------------
KNOWLEDGE_BASE = {
    "return_policy": "Customers can return unused items within 30 days for a 100% refund. After 30 days, a 15% restocking fee applies up to 60 days.",
    "vip_discount": "VIP Members receive a flat 20% discount on all purchases above $100.",
    "shipping_rates": "Standard shipping is $5.99. Orders over $50 qualify for free shipping. Express shipping is $14.99.",
    "product_macbook_pro": "MacBook Pro M3 16-inch: $2,499. In stock: 14 units.",
    "product_headphones": "Noise-Cancelling Pro Headphones: $199. In stock: 45 units."
}

def search_knowledge_base(query: str) -> str:
    """Search internal company policies and product information.
    Example: search_knowledge_base('return_policy')
    """
    query_clean = query.strip().lower().replace(" ", "_")
    for key, val in KNOWLEDGE_BASE.items():
        if key in query_clean or any(k in key for k in query_clean.split("_")):
            return val
    # Fallback to key word matching
    for key, val in KNOWLEDGE_BASE.items():
        words = query_clean.split("_")
        if any(w in val.lower() for w in words if len(w) > 3):
            return val
    return "No matching information found in the knowledge base."

# -----------------------------------------------------------------------------
# 4. Currency Conversion Tool
# -----------------------------------------------------------------------------
RATES_TO_USD = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.28,
    "JPY": 0.0067,
    "INR": 0.012,
    "CAD": 0.74,
    "AUD": 0.65
}

def convert_currency(amount: float, from_curr: str, to_curr: str) -> str:
    """Convert an amount from one currency to another.
    Example: convert_currency(100, 'USD', 'EUR')
    """
    try:
        from_c = from_curr.strip().upper()
        to_c = to_curr.strip().upper()
        amt = float(amount)
        if from_c not in RATES_TO_USD or to_c not in RATES_TO_USD:
            return f"Error: Supported currencies are {', '.join(RATES_TO_USD.keys())}"
        
        # Convert to USD first, then to target
        usd_val = amt * RATES_TO_USD[from_c]
        target_val = usd_val / RATES_TO_USD[to_c]
        return f"{amt} {from_c} = {target_val:.2f} {to_c}"
    except Exception as e:
        return f"Error converting currency: {str(e)}"

# -----------------------------------------------------------------------------
# Tool Registry & Schemas
# -----------------------------------------------------------------------------
TOOL_REGISTRY: Dict[str, Callable] = {
    "calculator": calculator,
    "get_weather": get_weather,
    "search_knowledge_base": search_knowledge_base,
    "convert_currency": convert_currency,
}

TOOL_DESCRIPTIONS = """
1. calculator(expression: str) -> str
   Safely evaluates mathematical expressions like "1500 * 45", "100 * (1 - 0.20)", etc.

2. get_weather(city: str) -> str
   Fetches current weather temperature and conditions for any city.

3. search_knowledge_base(query: str) -> str
   Searches company knowledge base (return policy, VIP discount, shipping, products).

4. convert_currency(amount: float, from_curr: str, to_curr: str) -> str
   Converts between USD, EUR, GBP, JPY, INR, CAD, AUD.
"""

def execute_tool(tool_name: str, **kwargs) -> str:
    """Execute a registered tool by name with arguments."""
    tool_name = tool_name.strip()
    if tool_name not in TOOL_REGISTRY:
        return f"Error: Tool '{tool_name}' not found. Available tools: {list(TOOL_REGISTRY.keys())}"
    try:
        func = TOOL_REGISTRY[tool_name]
        return str(func(**kwargs))
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"

# OpenAI function calling format definitions
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate mathematical expressions (multiplication, addition, percentages, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The math expression e.g. '1500 * 45 * 0.90'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather condition and temperature for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Name of the city, e.g. Tokyo"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Look up company policies, VIP discounts, return rules, and product catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Topic or keyword e.g. 'return_policy', 'vip_discount'"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert currency amounts between USD, EUR, GBP, JPY, INR, CAD, AUD",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "The numerical amount to convert"},
                    "from_curr": {"type": "string", "description": "Source currency symbol (e.g. USD)"},
                    "to_curr": {"type": "string", "description": "Target currency symbol (e.g. EUR)"}
                },
                "required": ["amount", "from_curr", "to_curr"]
            }
        }
    }
]
