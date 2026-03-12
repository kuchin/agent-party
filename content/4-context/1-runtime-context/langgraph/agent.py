from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)

# mock database — in production these are real queries
ORDERS = {
    "user_123": [
        {"id": "ORD_99", "item": "Laptop Stand", "status": "shipped"},
        {"id": "ORD_100", "item": "USB Hub", "status": "processing"},
    ],
}

@dataclass
class UserContext:
    user_id: str

# status is chosen by the LLM — user_id comes from your app (auth, session, etc.)
# ToolRuntime is hidden from the LLM — it can't see or fabricate user_id
@tool
def get_orders(status: str, runtime: ToolRuntime) -> str:
    """Get orders filtered by status."""
    user_id = runtime.context.user_id
    print(f"-> call: get_orders({status}) for {user_id}")
    matches = [o for o in ORDERS[user_id] if o["status"] == status]
    result = ", ".join(f'{o["id"]}: {o["item"]}' for o in matches) or "No orders found."
    print(f"-> result: {result}")
    return result

agent = create_agent(model, [get_orders], context_schema=UserContext)
result = agent.invoke(
    {"messages": [("user", "Do I have any shipped orders?")]},
    context=UserContext(user_id="user_123"),
)
print(result["messages"][-1].content)
# -> call: get_orders(shipped) for user_123
# -> result: ORD_99: Laptop Stand
# "Your shipped order is ORD_99: Laptop Stand."
