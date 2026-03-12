from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# token-aware: count tokens and only trim when approaching context limit
# Gemini supports up to 2M tokens — trimming is less urgent but still
# good practice for long-running conversations
WINDOW = 10
TOKEN_LIMIT = 100_000
history: list[types.Content] = []

def chat(message: str) -> str:
    history.append(types.Content(role="user", parts=[types.Part(text=message)]))
    # count actual tokens — no guessing needed
    token_count = client.models.count_tokens(
        model=LLM_MODEL, contents=history,
    )
    window = history
    if token_count.total_tokens > TOKEN_LIMIT:
        window = history[-WINDOW:]  # approaching limit — keep recent only
    response = client.models.generate_content(
        model=LLM_MODEL, contents=window,
    )
    history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
    return response.text

print(chat("What is the capital of France?"))
print(chat("What is its population?"))
