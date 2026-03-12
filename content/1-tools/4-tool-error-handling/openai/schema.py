# equivalent raw tool schema — what to_tool() + Pydantic generates
# replaces: GetWeatherParams, to_tool(), registry

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
            },
            "required": ["city"],
        },
    },
]

# dispatch tool calls manually:
# result = get_weather(**json.loads(tc.arguments))
