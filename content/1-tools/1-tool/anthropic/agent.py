import anthropic

LLM_MODEL = "claude-opus-4-6"

client = anthropic.Anthropic()

def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    print(f"-> call: get_weather({city})")
    result = f"The weather in {city} is 72°F and sunny."
    print(f"-> result: {result}")
    return result

tools = [{
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
        },
        "required": ["city"],
    },
}]

messages = [{"role": "user", "content": "What's the weather in Paris?"}]

# step 1: LLM decides to call the tool
response = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
)
# block.input is already a dict — no json.loads needed
tool_block = next(b for b in response.content if b.type == "tool_use")
result = get_weather(**tool_block.input)

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
# -> call: get_weather(Paris)
# -> result: The weather in Paris is 72°F and sunny.
# "It's 72°F and sunny in Paris."
