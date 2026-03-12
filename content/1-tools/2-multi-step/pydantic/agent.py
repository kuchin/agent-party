from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"

agent = Agent(LLM_MODEL)

CUSTOMERS = {"alice@example.com": "CUS_8f3a2b"}
BALANCES = {"CUS_8f3a2b": "$1,432.50"}

@agent.tool_plain
def lookup_customer(email: str) -> str:
    """Look up a customer by email and return their internal ID."""
    print(f"-> call: lookup_customer({email})")
    result = CUSTOMERS[email]
    print(f"-> result: {result}")
    return result

@agent.tool_plain
def get_balance(customer_id: str) -> str:
    """Get the account balance for a customer ID."""
    print(f"-> call: get_balance({customer_id})")
    result = BALANCES[customer_id]
    print(f"-> result: {result}")
    return result

# the LLM must call lookup_customer first to get the ID,
# then pass it to get_balance — a true data dependency
result = agent.run_sync("What's the balance for alice@example.com?")
print(result.output)
# -> call: lookup_customer(alice@example.com)
# -> result: CUS_8f3a2b
# -> call: get_balance(CUS_8f3a2b)
# -> result: $1,432.50
# "The balance for alice@example.com is $1,432.50."
