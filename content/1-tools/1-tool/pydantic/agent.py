from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"

agent = Agent(LLM_MODEL)

# @agent.tool_plain registers a function the LLM can call
# docstring → tool description, type hints → input schema
@agent.tool_plain
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    print(f"-> call: get_weather({city})")
    result = f"The weather in {city} is 72°F and sunny."
    print(f"-> result: {result}")
    return result

result = agent.run_sync("What's the weather in Paris?")
print(result.output)
# -> call: get_weather(Paris)
# -> result: The weather in Paris is 72°F and sunny.
# "It's 72°F and sunny in Paris."
