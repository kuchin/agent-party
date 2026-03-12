import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

# turn 1
messages = [{"role": "user", "content": "What is the capital of France?"}]
response = client.messages.create(model=LLM_MODEL, max_tokens=1024, messages=messages)
print(response.content[0].text)
# "The capital of France is Paris."

# without history, the model can't resolve "its"
no_context = client.messages.create(
    model=LLM_MODEL, max_tokens=1024,
    messages=[{"role": "user", "content": "What is its population?"}],
)
print(no_context.content[0].text)
# "Could you clarify what 'its' refers to?"

# the API is stateless — pass the full conversation each call
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": "What is its population?"})

response = client.messages.create(model=LLM_MODEL, max_tokens=1024, messages=messages)
print(response.content[0].text)
# "The population of Paris is approximately 2.1 million..."
