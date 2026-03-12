import json
from openai import OpenAI

LLM_MODEL = "gpt-5.4"
client = OpenAI()

def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    print(f"-> call: get_weather({city})")
    result = f"The weather in {city} is 72°F and sunny."
    print(f"-> result: {result}")
    return result

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
        },
        "required": ["city"],
    },
}]

input = [{
    "role": "user",
    "content": "What's the weather in Paris?",
}]

# step 1: LLM decides to call the tool
response = client.responses.create(
    model=LLM_MODEL, input=input, tools=tools,
)
tool_call = next(i for i in response.output if i.type == "function_call")
result = get_weather(**json.loads(tool_call.arguments))

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
# -> call: get_weather(Paris)
# -> result: The weather in Paris is 72°F and sunny.
# "It's 72°F and sunny in Paris."
