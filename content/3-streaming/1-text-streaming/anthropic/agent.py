import anthropic

LLM_MODEL = "claude-opus-4-6"

client = anthropic.Anthropic()

# .messages.stream() returns a context manager with convenience iterators
with client.messages.stream(
    model=LLM_MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain what an API is in a few sentences."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
print()
# An API (Application Programming Interface) is a set of rules and protocols
# that allows different software applications to communicate with each other...
