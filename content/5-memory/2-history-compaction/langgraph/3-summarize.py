from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import MemorySaver

LLM_MODEL = "gpt-5.4"
SUMMARY_MODEL = "gpt-5-mini"  # cheap model for summaries

# built-in summarization middleware — compresses old messages automatically
# triggers when the conversation exceeds a token threshold
# keeps recent messages intact, summarizes everything older
# uses a cheap model for compression to minimize cost

agent = create_agent(
    model=LLM_MODEL,
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model=SUMMARY_MODEL,
            trigger=("tokens", 4000),      # compress when context exceeds 4k tokens
            keep=("messages", 10),         # preserve the 10 most recent messages
        ),
    ],
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "chat_1"}}

result = agent.invoke(
    {"messages": [("user", "What is the capital of France?")]},
    config=config,
)
print(result["messages"][-1].content)

result = agent.invoke(
    {"messages": [("user", "What is its population?")]},
    config=config,
)
print(result["messages"][-1].content)
