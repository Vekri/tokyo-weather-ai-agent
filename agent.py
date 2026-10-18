"""
agent.py - Core AI Agent Implementation using the ReAct (Reason + Act) Pattern.

Demonstrates step-by-step:
1. User Goal Received
2. Thought (Agent analyzes the objective and plans next step)
3. Action (Agent decides which tool to invoke and prepares parameters)
4. Observation (Agent inspects the tool execution result)
5. Repeat or Final Answer (Agent synthesizes the observation into a final answer)
"""

import os
import sys
import json
import time

# Ensure UTF-8 output on Windows PowerShell / CMD
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from dataclasses import dataclass, field
from typing import List, Dict, Any, Generator, Optional
from tools import TOOL_REGISTRY, execute_tool, OPENAI_TOOLS, TOOL_DESCRIPTIONS

@dataclass
class AgentStep:
    step_number: int
    step_type: str  # "GOAL", "THOUGHT", "ACTION", "OBSERVATION", "FINAL_ANSWER"
    title: str
    content: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[str] = None
    explanation: Optional[str] = None

class SimpleAgent:
    """A clean, educational AI Agent implementing the ReAct framework."""

    def __init__(self, mode: str = "simulated", api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.mode = mode  # "simulated" or "openai"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.history: List[Dict[str, Any]] = []

    def run_step_by_step(self, user_query: str) -> Generator[AgentStep, None, None]:
        """
        Yields each step of the agent's reasoning and execution loop
        so viewers can see the step-by-step process in real time.
        """
        step_counter = 1

        # Step 1: Receiving the Goal
        yield AgentStep(
            step_number=step_counter,
            step_type="GOAL",
            title="🎯 Goal Received",
            content=user_query,
            explanation="The agent accepts the user's task and initializes its memory context."
        )
        step_counter += 1

        if self.mode == "openai" and self.api_key:
            yield from self._run_openai_loop(user_query, start_step=step_counter)
        else:
            yield from self._run_simulated_loop(user_query, start_step=step_counter)

    # -------------------------------------------------------------------------
    # Mode 1: Simulated Step-by-Step Execution (For Video & Zero-Setup Demo)
    # -------------------------------------------------------------------------
    def _run_simulated_loop(self, query: str, start_step: int) -> Generator[AgentStep, None, None]:
        """
        Deterministic, realistic ReAct traces designed for clear video teaching.
        Guaranteed to work without API keys, zero rate limits, zero latency errors.
        """
        q_lower = query.lower()

        # SCENARIO 1: Financial / Sales Calculation with Discount & Tax
        if any(w in q_lower for w in ["revenue", "sales", "units", "discount", "tax", "macbook", "headphone"]):
            yield AgentStep(
                step_number=start_step,
                step_type="THOUGHT",
                title="🧠 Step 1: Reasoning & Planning",
                content="I need to calculate the total order price. First, let me check the VIP discount policy from the knowledge base to see if a discount applies.",
                explanation="The agent uses its reasoning module to break the problem into sub-tasks."
            )

            # Tool Call 1
            tool_name = "search_knowledge_base"
            tool_args = {"query": "vip_discount"}
            yield AgentStep(
                step_number=start_step + 1,
                step_type="ACTION",
                title=f"🛠️ Step 2: Selecting Tool [{tool_name}]",
                content=f"Calling `{tool_name}` with parameters: {json.dumps(tool_args)}",
                tool_name=tool_name,
                tool_args=tool_args,
                explanation="The agent selects the appropriate tool from its registry to gather needed facts."
            )

            tool_result = execute_tool(tool_name, **tool_args)
            yield AgentStep(
                step_number=start_step + 2,
                step_type="OBSERVATION",
                title="👁️ Step 3: Tool Observation",
                content=f"Result: \"{tool_result}\"",
                tool_result=tool_result,
                explanation="The agent observes the result: VIP members get 20% discount on orders above $100."
            )

            # Second cycle: Math calculation
            yield AgentStep(
                step_number=start_step + 3,
                step_type="THOUGHT",
                title="🧠 Step 4: Next Reasoning Step",
                content="Now I know there is a 20% discount. The base price is 50 units * $30 = $1,500. Applying a 20% discount gives $1,500 * 0.80 = $1,200. Plus 8% sales tax: $1,200 * 1.08. Let's use the calculator to compute the exact total.",
                explanation="The agent synthesizes the previous observation and plans the next mathematical action."
            )

            tool_name = "calculator"
            tool_args = {"expression": "(50 * 30 * 0.80) * 1.08"}
            yield AgentStep(
                step_number=start_step + 4,
                step_type="ACTION",
                title=f"🛠️ Step 5: Selecting Tool [{tool_name}]",
                content=f"Calling `{tool_name}` with expression: `(50 * 30 * 0.80) * 1.08`",
                tool_name=tool_name,
                tool_args=tool_args,
                explanation="Instead of hallucinating math, the agent delegates precise computation to the calculator tool."
            )

            math_result = execute_tool(tool_name, **tool_args)
            yield AgentStep(
                step_number=start_step + 5,
                step_type="OBSERVATION",
                title="👁️ Step 6: Tool Observation",
                content=f"Calculation output: {math_result}",
                tool_result=math_result,
                explanation="The calculator returned 1296.0."
            )

            # Final Answer
            yield AgentStep(
                step_number=start_step + 6,
                step_type="FINAL_ANSWER",
                title="✅ Step 7: Final Synthesized Answer",
                content=(
                    f"### Order Summary:\n"
                    f"- **Base Price**: 50 units × $30 = $1,500.00\n"
                    f"- **VIP Discount (20%)**: -$300.00 (Discounted: $1,200.00)\n"
                    f"- **Sales Tax (8%)**: +$96.00\n"
                    f"- **Final Total**: **${float(math_result):,.2f}**\n\n"
                    f"All calculations verified via the internal knowledge base policy and safe arithmetic evaluator."
                ),
                explanation="The agent has gathered all facts, executed all tools, and delivered the verified final answer."
            )

        # SCENARIO 2: Weather in Tokyo + Unit Conversion (Celsius to Fahrenheit)
        elif any(w in q_lower for w in ["weather", "tokyo", "temperature", "forecast", "fahrenheit"]):
            city = "Tokyo" if "tokyo" in q_lower else ("London" if "london" in q_lower else "San Francisco")
            
            yield AgentStep(
                step_number=start_step,
                step_type="THOUGHT",
                title="🧠 Step 1: Reasoning & Planning",
                content=f"The user wants current weather for {city} and the temperature in Fahrenheit. I first need to fetch the real-time weather data for {city}.",
                explanation="The agent identifies that it lacks real-time knowledge and must call a live weather API."
            )

            tool_name = "get_weather"
            tool_args = {"city": city}
            yield AgentStep(
                step_number=start_step + 1,
                step_type="ACTION",
                title=f"🛠️ Step 2: Selecting Tool [{tool_name}]",
                content=f"Calling `{tool_name}` with parameters: {json.dumps(tool_args)}",
                tool_name=tool_name,
                tool_args=tool_args,
                explanation="Executing external tool function."
            )

            weather_res = execute_tool(tool_name, **tool_args)
            yield AgentStep(
                step_number=start_step + 2,
                step_type="OBSERVATION",
                title="👁️ Step 3: Tool Observation",
                content=f"Observation: {weather_res}",
                tool_result=weather_res,
                explanation=f"Received current temperature for {city} in Celsius."
            )

            # Extract temp or default 18
            temp_c = 18 if city == "Tokyo" else (14 if city == "London" else 19)
            yield AgentStep(
                step_number=start_step + 3,
                step_type="THOUGHT",
                title="🧠 Step 4: Next Reasoning Step",
                content=f"The temperature is {temp_c}°C. To convert Celsius to Fahrenheit, the formula is (C × 9/5) + 32. I will invoke the calculator tool to evaluate ({temp_c} * 9/5) + 32.",
                explanation="The agent knows the mathematical formula and delegates the calculation to the tool."
            )

            tool_name = "calculator"
            calc_expr = f"({temp_c} * 9 / 5) + 32"
            tool_args = {"expression": calc_expr}
            yield AgentStep(
                step_number=start_step + 4,
                step_type="ACTION",
                title=f"🛠️ Step 5: Selecting Tool [{tool_name}]",
                content=f"Calling `{tool_name}` with expression: `{calc_expr}`",
                tool_name=tool_name,
                tool_args=tool_args,
                explanation="Calculating Fahrenheit temperature with precision."
            )

            temp_f = execute_tool(tool_name, **tool_args)
            yield AgentStep(
                step_number=start_step + 5,
                step_type="OBSERVATION",
                title="👁️ Step 6: Tool Observation",
                content=f"Observation: {temp_f}°F",
                tool_result=temp_f,
                explanation="Accurate temperature conversion completed."
            )

            yield AgentStep(
                step_number=start_step + 6,
                step_type="FINAL_ANSWER",
                title="✅ Step 7: Final Synthesized Answer",
                content=(
                    f"### Weather Report for {city}:\n"
                    f"- **Condition**: Partly Cloudy with light winds\n"
                    f"- **Temperature**: **{temp_c}°C** (**{temp_f}°F**)\n"
                    f"- **Humidity**: 62%\n\n"
                    f"*Report generated dynamically via live weather lookup and unit conversion tools.*"
                ),
                explanation="The agent combines live API results and exact calculations into a complete response."
            )

        # SCENARIO 3: Return Policy & Restocking Fee / Customer Support
        elif any(w in q_lower for w in ["return", "refund", "policy", "restocking", "customer"]):
            yield AgentStep(
                step_number=start_step,
                step_type="THOUGHT",
                title="🧠 Step 1: Reasoning & Planning",
                content="The customer is asking about returning an item after 45 days. I need to look up company return policy rules in the internal knowledge base.",
                explanation="Agent searches enterprise documentation."
            )

            tool_name = "search_knowledge_base"
            tool_args = {"query": "return_policy"}
            yield AgentStep(
                step_number=start_step + 1,
                step_type="ACTION",
                title=f"🛠️ Step 2: Selecting Tool [{tool_name}]",
                content=f"Calling `{tool_name}` with parameters: {json.dumps(tool_args)}",
                tool_name=tool_name,
                tool_args=tool_args,
                explanation="Looking up policy documentation."
            )

            policy_res = execute_tool(tool_name, **tool_args)
            yield AgentStep(
                step_number=start_step + 2,
                step_type="OBSERVATION",
                title="👁️ Step 3: Tool Observation",
                content=f"Observation: \"{policy_res}\"",
                tool_result=policy_res,
                explanation="Policy found: 30 days = 100% refund. 31-60 days = 15% restocking fee."
            )

            yield AgentStep(
                step_number=start_step + 3,
                step_type="THOUGHT",
                title="🧠 Step 4: Next Reasoning Step",
                content="The item was purchased 45 days ago (between 30 and 60 days), so a 15% restocking fee applies. For a $200 item, the fee is 200 * 0.15 = $30, and the refund is 200 * 0.85 = $170. Let me confirm this via the calculator tool.",
                explanation="Agent applies business rules to customer context."
            )

            tool_name = "calculator"
            tool_args = {"expression": "200 * (1 - 0.15)"}
            yield AgentStep(
                step_number=start_step + 4,
                step_type="ACTION",
                title=f"🛠️ Step 5: Selecting Tool [{tool_name}]",
                content=f"Calling `{tool_name}` with expression: `200 * (1 - 0.15)`",
                tool_name=tool_name,
                tool_args=tool_args,
                explanation="Computing exact refund after restocking deduction."
            )

            refund_amt = execute_tool(tool_name, **tool_args)
            yield AgentStep(
                step_number=start_step + 5,
                step_type="OBSERVATION",
                title="👁️ Step 6: Tool Observation",
                content=f"Calculated Refund: ${refund_amt}",
                tool_result=refund_amt,
                explanation="Calculation verified."
            )

            yield AgentStep(
                step_number=start_step + 6,
                step_type="FINAL_ANSWER",
                title="✅ Step 7: Final Synthesized Answer",
                content=(
                    f"### Return Policy Assessment:\n"
                    f"- **Eligibility**: Under our policy, returns between 31 and 60 days are eligible with a **15% restocking fee**.\n"
                    f"- **Original Item Value**: $200.00\n"
                    f"- **Restocking Fee (15%)**: $30.00\n"
                    f"- **Total Refund Due**: **${float(refund_amt):.2f}**\n\n"
                    f"A return shipping label has been prepared."
                ),
                explanation="Complete enterprise customer resolution achieved."
            )

        # SCENARIO 4: General Dynamic Math / Fallback Evaluator
        else:
            yield AgentStep(
                step_number=start_step,
                step_type="THOUGHT",
                title="🧠 Step 1: Reasoning & Planning",
                content=f"I received the query: '{query}'. Let me analyze what tools are needed to answer accurately.",
                explanation="Evaluating general query."
            )

            # Try to extract numbers or math
            import re
            math_match = re.findall(r'[\d\.\+\-\*\/\(\)\s]{3,}', query)
            clean_math = math_match[0].strip() if math_match else "42 * 10"

            yield AgentStep(
                step_number=start_step + 1,
                step_type="ACTION",
                title="🛠️ Step 2: Selecting Tool [calculator]",
                content=f"Evaluating mathematical component: `{clean_math}`",
                tool_name="calculator",
                tool_args={"expression": clean_math},
                explanation="Delegating calculation to math engine."
            )

            res = execute_tool("calculator", expression=clean_math)
            yield AgentStep(
                step_number=start_step + 2,
                step_type="OBSERVATION",
                title="👁️ Step 3: Tool Observation",
                content=f"Result: {res}",
                tool_result=res,
                explanation="Computed value returned."
            )

            yield AgentStep(
                step_number=start_step + 3,
                step_type="FINAL_ANSWER",
                title="✅ Step 4: Final Synthesized Answer",
                content=f"Based on the analysis and tool evaluations for '{query}', the calculated outcome is **{res}**.",
                explanation="Agent finalized output."
            )

    # -------------------------------------------------------------------------
    # Mode 2: Live OpenAI API ReAct Execution (When API key is supplied)
    # -------------------------------------------------------------------------
    def _run_openai_loop(self, query: str, start_step: int) -> Generator[AgentStep, None, None]:
        """Real LLM call with OpenAI Function Calling loop."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
        except Exception as e:
            yield AgentStep(
                step_number=start_step,
                step_type="FINAL_ANSWER",
                title="⚠️ OpenAI Initialization Error",
                content=f"Could not initialize OpenAI client: {e}. Falling back to Simulated Mode."
            )
            yield from self._run_simulated_loop(query, start_step + 1)
            return

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert AI agent. Always reason step-by-step before invoking any tool. "
                    "Use tools whenever you need calculations, real-time data, or policy checks. "
                    "Never hallucinate mathematical results; always use the calculator tool."
                )
            },
            {"role": "user", "content": query}
        ]

        step_counter = start_step
        max_turns = 5

        for _ in range(max_turns):
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=OPENAI_TOOLS,
                tool_choice="auto"
            )

            choice = response.choices[0]
            message = choice.message

            # Check if LLM has reasoning or text
            if message.content:
                yield AgentStep(
                    step_number=step_counter,
                    step_type="THOUGHT",
                    title=f"🧠 Step {step_counter}: Agent Thought",
                    content=message.content,
                    explanation="LLM reasoning generated by live model."
                )
                step_counter += 1

            # Check if LLM requested tool calls
            if message.tool_calls:
                messages.append(message)
                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    try:
                        fn_args = json.loads(tool_call.function.arguments)
                    except:
                        fn_args = {"raw": tool_call.function.arguments}

                    yield AgentStep(
                        step_number=step_counter,
                        step_type="ACTION",
                        title=f"🛠️ Step {step_counter}: Action [{fn_name}]",
                        content=f"Tool: `{fn_name}`\nArguments: `{json.dumps(fn_args, indent=2)}`",
                        tool_name=fn_name,
                        tool_args=fn_args,
                        explanation="LLM chose to call a tool."
                    )
                    step_counter += 1

                    # Execute the tool
                    tool_result = execute_tool(fn_name, **fn_args)
                    yield AgentStep(
                        step_number=step_counter,
                        step_type="OBSERVATION",
                        title=f"👁️ Step {step_counter}: Tool Observation",
                        content=f"Observation: {tool_result}",
                        tool_result=tool_result,
                        explanation="Result fed back into LLM memory."
                    )
                    step_counter += 1

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": fn_name,
                        "content": str(tool_result)
                    })
            else:
                # No more tools, final response reached
                yield AgentStep(
                    step_number=step_counter,
                    step_type="FINAL_ANSWER",
                    title=f"✅ Step {step_counter}: Final Answer",
                    content=message.content or "Task completed.",
                    explanation="Final answer synthesized by model."
                )
                break
