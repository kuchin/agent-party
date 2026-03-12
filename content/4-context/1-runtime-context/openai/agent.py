import json
from openai import OpenAI

LLM_MODEL = "gpt-5.4"
client = OpenAI()

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
    "type": "function",
    "name": "get_orders",
    "description": "Get orders filtered by status.",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
        },
        "required": ["status"],
    },
}]

input = [{"role": "user", "content": "Do I have any shipped orders?"}]

# step 1: LLM decides to call the tool
response = client.responses.create(
    model=LLM_MODEL, input=input, tools=tools,
)
tool_call = next(i for i in response.output if i.type == "function_call")
result = get_orders(**json.loads(tool_call.arguments))

# step 2: send tool result back, LLM generates final response
input += response.output
input.append({
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": result,
})

response = client.responses.create(
    model=LLM_MODEL, input=input, tools=tools,
)
print(response.output_text)
# -> call: get_orders(shipped) for user_123
# -> result: ORD_99: Laptop Stand
# "Your shipped order is ORD_99: Laptop Stand."
