import json
from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# same multi-step tools: lookup_customer -> get_balance
CUSTOMERS = {"alice@example.com": "CUS_8f3a2b"}
BALANCES = {"CUS_8f3a2b": "$1,432.50"}

def lookup_customer(email: str) -> str:
    """Look up a customer by email and return their internal ID."""
    return CUSTOMERS[email]

def get_balance(customer_id: str) -> str:
    """Get the account balance for a customer ID."""
    return BALANCES[customer_id]

registry = {"lookup_customer": lookup_customer, "get_balance": get_balance}

# disable automatic function calling to observe events manually
# (AFC would execute tools internally, hiding them from the stream)
config = types.GenerateContentConfig(
    tools=[lookup_customer, get_balance],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True,
    ),
)

contents = ["What's the balance for alice@example.com?"]

# stream the full agent lifecycle: tool calls, results, and final text
while True:
    func_calls = []
    model_parts = []
    for chunk in client.models.generate_content_stream(
        model=LLM_MODEL, config=config, contents=contents,
    ):
        for part in (chunk.candidates[0].content.parts if chunk.candidates else []):
            if part.function_call:
                fc = part.function_call
                print(f"-> call: {fc.name}({json.dumps(dict(fc.args))})")
                func_calls.append(fc)
                model_parts.append(part)
            elif part.text:
                print(part.text, end="", flush=True)
    if not func_calls:
        break
    # preserve original parts (includes thought_signature required by API)
    contents.append(types.Content(role="model", parts=model_parts))
    tool_parts = []
    for fc in func_calls:
        result = registry[fc.name](**dict(fc.args))
        print(f"-> result: {result}")
        tool_parts.append(types.Part.from_function_response(
            name=fc.name, response={"result": result},
        ))
    contents.append(types.Content(role="tool", parts=tool_parts))
print()
# -> call: lookup_customer({"email": "alice@example.com"})
# -> result: CUS_8f3a2b
# -> call: get_balance({"customer_id": "CUS_8f3a2b"})
# -> result: $1,432.50
# The balance for alice@example.com is $1,432.50.
