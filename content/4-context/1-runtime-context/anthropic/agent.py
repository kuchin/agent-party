import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

# mock database — in production these are real queries
ORDERS = {
    "user_123": [
        {"id": "ORD_99", "item": "Laptop Stand", "status": "shipped"},
        {"id": "ORD_100", "item": "USB Hub", "status": "processing"},
    ],
}

# status is chosen by the LLM — user_id comes from your app (auth, session, etc.)
# only status appears in the tool schema — the LLM can't see or fabricate user_id
user_id = "user_123"

def get_orders(status: str) -> str:
    """Get orders filtered by status."""
    print(f"-> call: get_orders({status}) for {user_id}")
    matches = [o for o in ORDERS[user_id] if o["status"] == status]
    result = ", ".join(f'{o["id"]}: {o["item"]}' for o in matches) or "No orders found."
    print(f"-> result: {result}")
    return result

tools = [{
    "name": "get_orders",
    "description": "Get orders filtered by status.",
    "input_schema": {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
        },
        "required": ["status"],
    },
}]

messages = [{"role": "user", "content": "Do I have any shipped orders?"}]

# step 1: LLM decides to call the tool
response = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
)
tool_block = next(b for b in response.content if b.type == "tool_use")
result = get_orders(**tool_block.input)

# step 2: send tool result back, LLM generates final response
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": [{
    "type": "tool_result",
    "tool_use_id": tool_block.id,
    "content": result,
}]})

response = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
)
print(response.content[0].text)
# -> call: get_orders(shipped) for user_123
# -> result: ORD_99: Laptop Stand
# "Your shipped order is ORD_99: Laptop Stand."
