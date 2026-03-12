from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage

LLM_MODEL = "openai:gpt-5.4"

# token-aware: trim only when approaching the context window limit
# short conversations stay intact, long ones get pruned
# RunContext gives access to accumulated token usage

def token_trim(
    ctx: RunContext[None], messages: list[ModelMessage],
) -> list[ModelMessage]:
    if ctx.usage.total_tokens > 100_000:
        return messages[-10:]  # approaching limit — keep recent only
    return messages  # still fits — keep everything

agent = Agent(LLM_MODEL, history_processors=[token_trim])

history: list[ModelMessage] = []

result = agent.run_sync("What is the capital of France?", message_history=history)
history = result.new_messages()
print(result.output)

result = agent.run_sync("What is its population?", message_history=history)
history = result.new_messages()
print(result.output)
