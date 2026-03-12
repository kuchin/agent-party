# equivalent raw tool schema — same contract the SDK derives from the function
# replaces: passing Python function directly

from google.genai import types

tools = [types.Tool(function_declarations=[{
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
        },
        "required": ["city"],
    },
}])]

# with dict-declared tools, dispatch manually:
# tool_call = response.function_calls[0]
# result = get_weather(**tool_call.args)
