from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessageChunk, ToolMessage

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)

CUSTOMERS = {"alice@example.com": "CUS_8f3a2b"}
BALANCES = {"CUS_8f3a2b": "$1,432.50"}

@tool
def lookup_customer(email: str) -> str:
    """Look up a customer by email and return their internal ID."""
    return CUSTOMERS[email]

@tool
def get_balance(customer_id: str) -> str:
    """Get the account balance for a customer ID."""
    return BALANCES[customer_id]

agent = create_agent(model, [lookup_customer, get_balance])

# stream_mode="messages" emits tool calls, tool results, and text deltas
tool_name = ""
tool_args = ""
for chunk, metadata in agent.stream(
    {"messages": [("user", "What's the balance for alice@example.com?")]},
    stream_mode="messages",
):
    if isinstance(chunk, AIMessageChunk):
        # tool call args stream incrementally — accumulate them
        for tc in chunk.tool_call_chunks:
            if tc["name"]:
                tool_name = tc["name"]
                tool_args = tc.get("args", "") or ""
            else:
                tool_args += tc.get("args", "") or ""
        # text delta — stream to stdout
        if chunk.content and metadata["langgraph_node"] == "model":
            print(chunk.content, end="", flush=True)
    elif isinstance(chunk, ToolMessage):
        if tool_name:
            print(f"-> call: {tool_name}({tool_args})")
            tool_name = ""
            tool_args = ""
        print(f"-> result: {chunk.content}")
print()
# -> call: lookup_customer({"email": "alice@example.com"})
# -> result: CUS_8f3a2b
# -> call: get_balance({"customer_id": "CUS_8f3a2b"})
# -> result: $1,432.50
# The balance for alice@example.com is $1,432.50.
