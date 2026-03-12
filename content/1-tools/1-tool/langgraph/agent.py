from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

# docstring → tool description, type hints → input schema
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    print(f"-> call: get_weather({city})")
    result = f"The weather in {city} is 72°F and sunny."
    print(f"-> result: {result}")
    return result

# the agent runs the ReAct loop: LLM → tool call → LLM → response
agent = create_agent(model, [get_weather])
result = agent.invoke({
    "messages": [("user", "What's the weather in Paris?")]
})
print(result["messages"][-1].content)
# -> call: get_weather(Paris)
# -> result: The weather in Paris is 72°F and sunny.
# "It's 72°F and sunny in Paris."
