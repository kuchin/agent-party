from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)

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
class UserContext:
    user_id: str

# @dynamic_prompt middleware builds the system message from context at runtime
# the LLM sees personalized context without querying the database itself
@dynamic_prompt
def build_prompt(request):
    user_id = request.runtime.context.user_id
    customer = CUSTOMERS[user_id]
    overdue = OVERDUE_INVOICES[user_id]
    lines = [f"Customer: {customer['name']}, plan: {customer['plan']}."]
    if overdue:
        lines.append(
            f"ALERT: {len(overdue)} overdue invoice(s). Prioritize payment resolution."
        )
    if customer["plan"] == "enterprise":
        lines.append("This is a premium customer. Offer direct escalation.")
    return "\n".join(lines)

agent = create_agent(
    model, tools=[], middleware=[build_prompt], context_schema=UserContext,
)

# same agent, same question — behavior changes based on who's asking
result = agent.invoke(
    {"messages": [("user", "I need help with my account.")]},
    context=UserContext(user_id="user_123"),
)
print(result["messages"][-1].content)
# "I see there's an overdue invoice on your account. Let me help
#  resolve that. As a premium customer, I can escalate directly."

result = agent.invoke(
    {"messages": [("user", "I need help with my account.")]},
    context=UserContext(user_id="user_456"),
)
print(result["messages"][-1].content)
# "Sure, I'd be happy to help! What do you need assistance with?"
