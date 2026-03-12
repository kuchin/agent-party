from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

agent = create_agent(model, tools=[])

# stream_mode="messages" gives token-level deltas (not state updates)
for chunk, metadata in agent.stream(
    {"messages": [("user", "Explain what an API is in a few sentences.")]},
    stream_mode="messages",
):
    if hasattr(chunk, "content") and chunk.content:
        print(chunk.content, end="", flush=True)
print()
# An API (Application Programming Interface) is a set of rules and protocols
# that allows different software applications to communicate with each other...
