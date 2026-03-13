from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()

# two tools with a data dependency:
# lookup_customer returns an ID that get_balance needs

CUSTOMERS = {"alice@example.com": "CUS_8f3a2b"}
BALANCES = {"CUS_8f3a2b": "$1,432.50"}

def lookup_customer(email: str) -> str:
    """Look up a customer by email and return their internal ID."""
    print(f"-> call: lookup_customer({email})")
    result = CUSTOMERS[email]
    print(f"-> result: {result}")
    return result

def get_balance(customer_id: str) -> str:
    """Get the account balance for a customer ID."""
    print(f"-> call: get_balance({customer_id})")
    result = BALANCES[customer_id]
    print(f"-> result: {result}")
    return result

# same ReAct pattern, but Gemini's SDK runs the loop for you:
# model -> tool call -> tool result -> model
config = types.GenerateContentConfig(
    tools=[lookup_customer, get_balance],
)

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents="What's the balance for alice@example.com?",
)
print(response.text)
# -> call: lookup_customer(alice@example.com)
# -> result: CUS_8f3a2b
# -> call: get_balance(CUS_8f3a2b)
# -> result: $1,432.50
# "The balance for alice@example.com is $1,432.50."
