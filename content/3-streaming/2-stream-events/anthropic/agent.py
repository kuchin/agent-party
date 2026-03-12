import json
import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

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

tools = [
    {
        "name": "lookup_customer",
        "description": "Look up a customer by email and return their internal ID",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string"}},
            "required": ["email"],
        },
    },
    {
        "name": "get_balance",
        "description": "Get the account balance for a customer ID",
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
]

messages = [{"role": "user", "content": "What's the balance for alice@example.com?"}]

# stream the full agent lifecycle: tool calls, results, and final text
while True:
    with client.messages.stream(
        model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
    ) as stream:
        for event in stream:
            # completed tool_use block — print name and args
            if event.type == "content_block_stop" and event.content_block.type == "tool_use":
                tb = event.content_block
                print(f"-> call: {tb.name}({json.dumps(tb.input)})")
            # text delta — stream to stdout
            elif event.type == "text":
                print(event.text, end="", flush=True)
    response = stream.get_final_message()
    if response.stop_reason != "tool_use":
        break
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = registry[block.name](**block.input)
            print(f"-> result: {result}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
    messages.append({"role": "user", "content": tool_results})
print()
# -> call: lookup_customer({"email": "alice@example.com"})
# -> result: CUS_8f3a2b
# -> call: get_balance({"customer_id": "CUS_8f3a2b"})
# -> result: $1,432.50
# The balance for alice@example.com is $1,432.50.
