import asyncio
from openai import AsyncOpenAI

LLM_MODEL = "gpt-5.4"

client = AsyncOpenAI()

# Same Responses API as the sync example.
# The difference is the async client + await, which matters once this call lives
# inside an async web server, background worker, or many concurrent model calls.
async def main():
    response = await client.responses.create(
        model=LLM_MODEL,
        input="What is the capital of France?",
    )
    print(response.output_text)


asyncio.run(main())
# "Paris."
