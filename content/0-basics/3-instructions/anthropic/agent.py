import anthropic

LLM_MODEL = "claude-opus-4-6"

client = anthropic.Anthropic()

# system prompt is a top-level parameter, not a message
response = client.messages.create(
    model=LLM_MODEL,
    max_tokens=1024,
    system="You are a pirate. Always respond in pirate speak.",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(response.content[0].text)
# "Arrr, Paris be the capital, matey!"
