from openai import OpenAI

LLM_MODEL = "gpt-5.4"

client = OpenAI()

# stream=True returns typed server-sent events
stream = client.responses.create(
    model=LLM_MODEL,
    input="Explain what an API is in a few sentences.",
    stream=True,
)
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
print()
# An API (Application Programming Interface) is a set of rules and protocols
# that allows different software applications to communicate with each other...
