from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

LLM_MODEL = "openai:gpt-5.4"

# sliding window: keep last N messages, discard everything older
# processor runs before each model call, replaces history for that call
WINDOW = 10

def sliding_window(messages: list[ModelMessage]) -> list[ModelMessage]:
    return messages[-WINDOW:]

agent = Agent(LLM_MODEL, history_processors=[sliding_window])

history: list[ModelMessage] = []

result = agent.run_sync("What is the capital of France?", message_history=history)
history = result.new_messages()
print(result.output)

result = agent.run_sync("What is its population?", message_history=history)
history = result.new_messages()
print(result.output)
