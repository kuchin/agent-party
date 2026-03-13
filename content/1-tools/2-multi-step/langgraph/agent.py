from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

CUSTOMERS = {"alice@example.com": "CUS_8f3a2b"}
BALANCES = {"CUS_8f3a2b": "$1,432.50"}

@tool
def lookup_customer(email: str) -> str:
    """Look up a customer by email and return their internal ID."""
    print(f"-> call: lookup_customer({email})")
    result = CUSTOMERS[email]
    print(f"-> result: {result}")
    return result

@tool
def get_balance(customer_id: str) -> str:
    """Get the account balance for a customer ID."""
    print(f"-> call: get_balance({customer_id})")
    result = BALANCES[customer_id]
    print(f"-> result: {result}")
    return result

# this is the basic ReAct loop in graph form:
# model -> tool -> model -> tool -> model
agent = create_agent(model, [lookup_customer, get_balance])
result = agent.invoke({
    "messages": [("user", "What's the balance for alice@example.com?")]
})
print(result["messages"][-1].content)
# -> call: lookup_customer(alice@example.com)
# -> result: CUS_8f3a2b
# -> call: get_balance(CUS_8f3a2b)
# -> result: $1,432.50
# "The balance for alice@example.com is $1,432.50."
