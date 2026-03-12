from langchain.agents import create_agent
from langchain.agents.middleware import before_model
from langchain_openai import ChatOpenAI
from langchain_core.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import MemorySaver

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)

# sliding window: keep last N messages via @before_model middleware
# runs before every model call — trims checkpointed state in-place
WINDOW = 10

@before_model
def sliding_window(state, runtime):
    messages = state["messages"]
    if len(messages) <= WINDOW:
        return None  # short enough — no trimming needed
    # remove all, then re-add only the recent window
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *messages[-WINDOW:],
        ]
    }

agent = create_agent(
    model, tools=[], middleware=[sliding_window],
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
