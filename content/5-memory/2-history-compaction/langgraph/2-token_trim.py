from langchain.agents import create_agent
from langchain.agents.middleware import before_model
from langchain_openai import ChatOpenAI
from langchain_core.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import MemorySaver

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)

# token-aware: only trim when message count exceeds threshold
# short conversations stay intact — middleware returns None to skip
THRESHOLD = 50
WINDOW = 10

@before_model
def token_trim(state, runtime):
    messages = state["messages"]
    if len(messages) <= THRESHOLD:
        return None  # fits — keep everything
    # approaching limit — keep first message (system) + recent window
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            messages[0],
            *messages[-WINDOW:],
        ]
    }

agent = create_agent(
    model, tools=[], middleware=[token_trim],
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
