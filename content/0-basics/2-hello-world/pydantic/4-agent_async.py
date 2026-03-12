import asyncio
from pydantic_ai import Agent

# Same model string and same agent config as run_sync().
LLM_MODEL = "openai:gpt-5.4"

agent = Agent(LLM_MODEL)


# Async is useful when the caller already runs an event loop, or when this
# agent call needs to compose with async tools, HTTP requests, or DB work.
async def main():
    result = await agent.run("What is the capital of France?")
    print(result.output)


asyncio.run(main())
# "Paris."
