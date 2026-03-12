from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()

def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    print(f"-> call: get_weather({city})")
    result = f"The weather in {city} is 72°F and sunny."
    print(f"-> result: {result}")
    return result

# automatic function calling: SDK executes the tool and feeds results back
config = types.GenerateContentConfig(tools=[get_weather])

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents="What's the weather in Paris?",
)
print(response.text)
# -> call: get_weather(Paris)
# -> result: The weather in Paris is 72°F and sunny.
# "It's 72°F and sunny in Paris."
