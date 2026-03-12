import asyncio
from anthropic import AsyncAnthropic

LLM_MODEL = "claude-opus-4-6"

client = AsyncAnthropic()

# Same request payload as the sync client.
# Async mainly changes where this code fits: use it when the caller already has
# an event loop or needs to overlap Claude calls with other I/O.
async def main():
    response = await client.messages.create(
        model=LLM_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": "What is the capital of France?"}],
    )
    print(response.content[0].text)


asyncio.run(main())
# "Paris."
