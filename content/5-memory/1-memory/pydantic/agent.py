from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"
agent = Agent(LLM_MODEL)

# Pydantic AI has no built-in memory — store messages yourself
store: dict[str, list] = {}

def chat(thread_id: str, message: str) -> str:
    history = store.get(thread_id, [])
    result = agent.run_sync(message, message_history=history)
    store[thread_id] = result.new_messages()
    return result.output

# turn 1
print(chat("chat_1", "What is the capital of France?"))
# "The capital of France is Paris."

# turn 2 — same thread, history is restored from the store
print(chat("chat_1", "What is its population?"))
# "The population of Paris is approximately 2.1 million..."
