import asyncio
from pydantic_ai import Agent, ModelMessage

LLM_MODEL = "openai:gpt-5.4"
SUMMARY_MODEL = "openai:gpt-5-mini"  # cheap model for summaries

# summarization: compress old messages with a cheap model
# most expensive — adds latency and cost, but preserves context
# the processor fires before each model call automatically

summarize_agent = Agent(
    SUMMARY_MODEL,
    instructions="Summarize this conversation in 2-3 sentences. "
    "Preserve key facts, decisions, and open questions.",
)

async def summarize_old(messages: list[ModelMessage]) -> list[ModelMessage]:
    if len(messages) <= 10:
        return messages  # short enough — no compression needed
    oldest = messages[:-6]
    recent = messages[-6:]
    # pass structured messages via message_history — not a stringified prompt
    summary = await summarize_agent.run(message_history=oldest)
    # new_messages() returns properly formed ModelMessage objects
    return summary.new_messages() + recent

agent = Agent(LLM_MODEL, history_processors=[summarize_old])

async def main():
    history: list[ModelMessage] = []
    for prompt in [
        "What is the capital of France?",
        "What is its population?",
        "And the metro area?",
    ]:
        result = await agent.run(prompt, message_history=history)
        history = result.all_messages()
        print(result.output)

asyncio.run(main())
