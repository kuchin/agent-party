from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

LLM_MODEL = "openai:gpt-5.4"

# mock database — in production these are real queries
CUSTOMERS = {
    "user_123": {"name": "Acme Corp", "plan": "enterprise"},
    "user_456": {"name": "Jane Smith", "plan": "free"},
}
OVERDUE_INVOICES = {
    "user_123": [{"id": "INV-42", "amount": 1200}],
    "user_456": [],
}

@dataclass
class Deps:
    user_id: str

agent = Agent(LLM_MODEL, deps_type=Deps)

# instructions are built at request time from live data — not a static string
# the LLM sees personalized context without querying the database itself
@agent.instructions
def dynamic_instructions(ctx: RunContext[Deps]) -> str:
    customer = CUSTOMERS[ctx.deps.user_id]
    overdue = OVERDUE_INVOICES[ctx.deps.user_id]
    lines = [f"Customer: {customer['name']}, plan: {customer['plan']}."]
    if overdue:
        lines.append(
            f"ALERT: {len(overdue)} overdue invoice(s). Prioritize payment resolution."
        )
    if customer["plan"] == "enterprise":
        lines.append("This is a premium customer. Offer direct escalation.")
    return "\n".join(lines)

# same agent, same question — behavior changes based on who's asking
result = agent.run_sync(
    "I need help with my account.",
    deps=Deps(user_id="user_123"),
)
print(result.output)
# "I see there's an overdue invoice on your account. Let me help
#  resolve that. As a premium customer, I can escalate directly."

result = agent.run_sync(
    "I need help with my account.",
    deps=Deps(user_id="user_456"),
)
print(result.output)
# "Sure, I'd be happy to help! What do you need assistance with?"
