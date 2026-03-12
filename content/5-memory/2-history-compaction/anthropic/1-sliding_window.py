import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

# sliding window: keep last N messages, discard everything older
# cheapest — zero latency, but complete context loss beyond the window
WINDOW = 10
messages: list = []

def chat(message: str) -> str:
    messages.append({"role": "user", "content": message})
    # only send the last WINDOW messages
    window = messages[-WINDOW:]
    response = client.messages.create(
        model=LLM_MODEL, max_tokens=1024, messages=window,
    )
    messages.append({"role": "assistant", "content": response.content})
    return response.content[0].text

print(chat("What is the capital of France?"))
print(chat("What is its population?"))
