import anthropic

LLM_MODEL = "claude-opus-4-6"

client = anthropic.Anthropic()

response = client.messages.create(
    model=LLM_MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(response.content[0].text)
# "Paris."
