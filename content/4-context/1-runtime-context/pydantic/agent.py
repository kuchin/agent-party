from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

LLM_MODEL = "openai:gpt-5.4"

# mock database — in production these are real queries
ORDERS = {
    "user_123": [
        {"id": "ORD_99", "item": "Laptop Stand", "status": "shipped"},
        {"id": "ORD_100", "item": "USB Hub", "status": "processing"},
    ],
}

@dataclass
class Deps:
    user_id: str

agent = Agent(LLM_MODEL, deps_type=Deps)

# status is chosen by the LLM — user_id comes from your app (auth, session, etc.)
# RunContext is hidden from the LLM — it can't see or fabricate user_id
@agent.tool
def get_orders(ctx: RunContext[Deps], status: str) -> str:
    """Get orders filtered by status."""
    print(f"-> call: get_orders({status}) for {ctx.deps.user_id}")
    matches = [o for o in ORDERS[ctx.deps.user_id] if o["status"] == status]
    result = ", ".join(f'{o["id"]}: {o["item"]}' for o in matches) or "No orders found."
    print(f"-> result: {result}")
    return result

result = agent.run_sync(
    "Do I have any shipped orders?",
    deps=Deps(user_id="user_123"),
)
print(result.output)
# -> call: get_orders(shipped) for user_123
# -> result: ORD_99: Laptop Stand
# "Your shipped order is ORD_99: Laptop Stand."
