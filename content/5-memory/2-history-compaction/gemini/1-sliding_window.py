from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# sliding window: keep last N messages, discard everything older
# cheapest — zero latency, but complete context loss beyond the window
# can't use chat.send_message() here — it manages history internally
WINDOW = 10
history: list[types.Content] = []

def chat(message: str) -> str:
    history.append(types.Content(role="user", parts=[types.Part(text=message)]))
    window = history[-WINDOW:]
    response = client.models.generate_content(
        model=LLM_MODEL, contents=window,
    )
    history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
    return response.text

print(chat("What is the capital of France?"))
print(chat("What is its population?"))
