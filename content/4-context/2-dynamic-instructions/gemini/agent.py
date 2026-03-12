from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# mock database — in production these are real queries
CUSTOMERS = {
    "user_123": {"name": "Acme Corp", "plan": "enterprise"},
    "user_456": {"name": "Jane Smith", "plan": "free"},
}
OVERDUE_INVOICES = {
    "user_123": [{"id": "INV-42", "amount": 1200}],
    "user_456": [],
}

# instructions are built at request time from live data — not a static string
# the LLM sees personalized context without querying the database itself
def build_instructions(user_id: str) -> str:
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

# same agent, same question — behavior changes based on who's asking
response = client.models.generate_content(
    model=LLM_MODEL,
    config=types.GenerateContentConfig(
        system_instruction=build_instructions("user_123"),
    ),
    contents="I need help with my account.",
)
print(response.text)
# "I see there's an overdue invoice on your account. Let me help
#  resolve that. As a premium customer, I can escalate directly."

response = client.models.generate_content(
    model=LLM_MODEL,
    config=types.GenerateContentConfig(
        system_instruction=build_instructions("user_456"),
    ),
    contents="I need help with my account.",
)
print(response.text)
# "Sure, I'd be happy to help! What do you need assistance with?"
