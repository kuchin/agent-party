from openai import OpenAI

LLM_MODEL = "gpt-5.4"
client = OpenAI()

# token-aware compaction: API auto-compresses when input exceeds threshold
# old assistant messages and tool calls are replaced with encrypted compaction
# items — user messages are always kept verbatim

response = client.responses.create(
    model=LLM_MODEL,
    input="What is the capital of France?",
)
print(response.output_text)

# context_management auto-triggers compaction when tokens exceed threshold
response = client.responses.create(
    model=LLM_MODEL,
    previous_response_id=response.id,
    input=[{"role": "user", "content": "What is its population?"}],
    context_management=[
        {"type": "compaction", "compact_threshold": 100_000}
    ],
)
print(response.output_text)
