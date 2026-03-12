import anthropic

LLM_MODEL = "claude-opus-4-6"

client = anthropic.Anthropic()

# two tools with a data dependency:
# lookup_customer returns an ID that get_balance needs

CUSTOMERS = {"alice@example.com": "CUS_8f3a2b"}
BALANCES = {"CUS_8f3a2b": "$1,432.50"}

def lookup_customer(email: str) -> str:
    """Look up a customer by email and return their internal ID."""
    print(f"-> call: lookup_customer({email})")
    result = CUSTOMERS[email]
    print(f"-> result: {result}")
    return result

def get_balance(customer_id: str) -> str:
    """Get the account balance for a customer ID."""
    print(f"-> call: get_balance({customer_id})")
    result = BALANCES[customer_id]
    print(f"-> result: {result}")
    return result

# build tool schema and register for dispatch
registry = {}

def to_tool(fn, input_schema):
    registry[fn.__name__] = fn
    return {
        "name": fn.__name__,
        "description": fn.__doc__,
        "input_schema": input_schema,
    }

tools = [
    to_tool(lookup_customer, {
        "type": "object",
        "properties": {"email": {"type": "string"}},
        "required": ["email"],
    }),
    to_tool(get_balance, {
        "type": "object",
        "properties": {"customer_id": {"type": "string"}},
        "required": ["customer_id"],
    }),
]

messages = [{"role": "user", "content": "What's the balance for alice@example.com?"}]

# ReAct loop: LLM calls tools until it can answer
while True:
    response = client.messages.create(
        model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
    )
    if response.stop_reason != "tool_use":
        break
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = registry[block.name](**block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
    messages.append({"role": "user", "content": tool_results})

print(response.content[0].text)
# -> call: lookup_customer(alice@example.com)
# -> result: CUS_8f3a2b
# -> call: get_balance(CUS_8f3a2b)
# -> result: $1,432.50
# "The balance for alice@example.com is $1,432.50."
