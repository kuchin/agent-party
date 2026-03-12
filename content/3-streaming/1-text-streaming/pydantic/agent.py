from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"

agent = Agent(LLM_MODEL)

# stream_text(delta=True) yields each token as it arrives
result = agent.run_stream_sync(
    "Explain what an API is in a few sentences.",
)
for text in result.stream_text(delta=True):
    print(text, end="", flush=True)
print()
# An API (Application Programming Interface) is a set of rules and protocols
# that allows different software applications to communicate with each other...
