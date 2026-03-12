import json
from openai import OpenAI
from pydantic import BaseModel

LLM_MODEL = "gpt-5.4"
client = OpenAI()

# same multi-step tools: lookup_customer -> get_balance
CUSTOMERS = {"alice@example.com": "CUS_8f3a2b"}
BALANCES = {"CUS_8f3a2b": "$1,432.50"}

def lookup_customer(email: str) -> str:
    """Look up a customer by email and return their internal ID."""
    return CUSTOMERS[email]

def get_balance(customer_id: str) -> str:
    """Get the account balance for a customer ID."""
    return BALANCES[customer_id]

class LookupCustomerParams(BaseModel):
    email: str

class GetBalanceParams(BaseModel):
    customer_id: str

registry = {}

def to_tool(fn, params):
    registry[fn.__name__] = fn
    return {
        "type": "function",
        "name": fn.__name__,
        "description": fn.__doc__,
        "parameters": params.model_json_schema(),
    }

tools = [
    to_tool(lookup_customer, LookupCustomerParams),
    to_tool(get_balance, GetBalanceParams),
]

input = [{"role": "user", "content": "What's the balance for alice@example.com?"}]

# stream the full agent lifecycle: tool calls, results, and final text
while True:
    stream = client.responses.create(
        model=LLM_MODEL, input=input, tools=tools, stream=True,
    )
    tool_calls = []
    output_items = []
    for event in stream:
        # completed output item — collect for next round
        if event.type == "response.output_item.done":
            output_items.append(event.item)
            if event.item.type == "function_call":
                tc = event.item
                print(f"-> call: {tc.name}({tc.arguments})")
                result = registry[tc.name](**json.loads(tc.arguments))
                print(f"-> result: {result}")
                tool_calls.append((tc, result))
        # text delta — stream to stdout
        elif event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    if not tool_calls:
        break
    input += output_items
    for tc, result in tool_calls:
        input.append({
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": result,
        })
print()
# -> call: lookup_customer({"email":"alice@example.com"})
# -> result: CUS_8f3a2b
# -> call: get_balance({"customer_id":"CUS_8f3a2b"})
# -> result: $1,432.50
# The balance for alice@example.com is $1,432.50.
