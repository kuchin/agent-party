import asyncio
from google import genai

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()

# Gemini keeps one client; the async surface hangs off client.aio.
# So the prompt and model stay the same, but the model call becomes awaitable.
async def main():
    response = await client.aio.models.generate_content(
        model=LLM_MODEL,
        contents="What is the capital of France?",
    )
    print(response.text)


asyncio.run(main())
# "Paris."
