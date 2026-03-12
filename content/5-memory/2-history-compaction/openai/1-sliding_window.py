from openai import OpenAI

LLM_MODEL = "gpt-5.4"
client = OpenAI()

# sliding window: keep last N messages, discard everything older
# cheapest — zero latency, but complete context loss beyond the window
WINDOW = 10
messages: list = []

def chat(message: str) -> str:
    messages.append({"role": "user", "content": message})
    # only send the last WINDOW messages
    window = messages[-WINDOW:]
    response = client.responses.create(model=LLM_MODEL, input=window)
    messages.append({"role": "assistant", "content": response.output_text})
    return response.output_text

print(chat("What is the capital of France?"))
print(chat("What is its population?"))
