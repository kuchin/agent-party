import asyncio
import json
from pydantic_ai import Agent
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartStartEvent,
    PartDeltaEvent,
    TextPart,
    TextPartDelta,
)

LLM_MODEL = "openai:gpt-5.4"

agent = Agent(LLM_MODEL)

CUSTOMERS = {"alice@example.com": "CUS_8f3a2b"}
BALANCES = {"CUS_8f3a2b": "$1,432.50"}

@agent.tool_plain
def lookup_customer(email: str) -> str:
    """Look up a customer by email and return their internal ID."""
    return CUSTOMERS[email]

@agent.tool_plain
def get_balance(customer_id: str) -> str:
    """Get the account balance for a customer ID."""
    return BALANCES[customer_id]


# run_stream_events yields every lifecycle event — no manual loop needed
async def main():
    async for event in agent.run_stream_events(
        "What's the balance for alice@example.com?",
    ):
        if isinstance(event, FunctionToolCallEvent):
            args = json.dumps(event.part.args) if isinstance(event.part.args, dict) else event.part.args
            print(f"-> call: {event.part.tool_name}({args})")
        elif isinstance(event, FunctionToolResultEvent):
            print(f"-> result: {event.result.content}")
        elif isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
            print(event.part.content, end="", flush=True)
        elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
            print(event.delta.content_delta, end="", flush=True)
    print()


asyncio.run(main())
# -> call: lookup_customer({"email": "alice@example.com"})
# -> result: CUS_8f3a2b
# -> call: get_balance({"customer_id": "CUS_8f3a2b"})
# -> result: $1,432.50
# The balance for alice@example.com is $1,432.50.
