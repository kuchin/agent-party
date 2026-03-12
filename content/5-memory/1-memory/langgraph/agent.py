from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)

# checkpointer persists state — same thread_id restores history
checkpointer = MemorySaver()
agent = create_agent(model, tools=[], checkpointer=checkpointer)

config = {"configurable": {"thread_id": "chat_1"}}

# turn 1
result = agent.invoke(
    {"messages": [("user", "What is the capital of France?")]},
    config=config,
)
print(result["messages"][-1].content)
# "The capital of France is Paris."

# turn 2 — same thread_id, checkpointer restores history automatically
result = agent.invoke(
    {"messages": [("user", "What is its population?")]},
    config=config,
)
print(result["messages"][-1].content)
# "The population of Paris is approximately 2.1 million..."
