import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

# Anthropic has no built-in memory — store messages yourself
store: dict[str, list] = {}

def chat(thread_id: str, message: str) -> str:
    history = store.get(thread_id, [])
    history.append({"role": "user", "content": message})
    response = client.messages.create(
        model=LLM_MODEL, max_tokens=1024, messages=history,
    )
    history.append({"role": "assistant", "content": response.content})
    store[thread_id] = history
    return response.content[0].text

# turn 1
print(chat("chat_1", "What is the capital of France?"))
# "The capital of France is Paris."

# turn 2 — same thread, history is restored from the store
print(chat("chat_1", "What is its population?"))
# "The population of Paris is approximately 2.1 million..."
