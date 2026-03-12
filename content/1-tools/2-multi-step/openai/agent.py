import json
from openai import OpenAI
from pydantic import BaseModel

LLM_MODEL = "gpt-5.4"
client = OpenAI()

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

class LookupCustomerParams(BaseModel):
    email: str

class GetBalanceParams(BaseModel):
    customer_id: str

# build tool schema and register for dispatch
registry = {}

def to_tool(fn, params):
    registry[fn.__name__] = fn
    return {
        "type": "function",
        "name": fn.__name__,
        "description": fn.__doc__,
        "parameters": params.model_json_schema(),
    }

tools = [
    to_tool(lookup_customer, LookupCustomerParams),
    to_tool(get_balance, GetBalanceParams),
]

input = [{
    "role": "user",
    "content": "What's the balance for alice@example.com?",
}]

# ReAct loop: LLM calls tools until it can answer
while True:
    response = client.responses.create(
        model=LLM_MODEL, input=input, tools=tools,
    )
    tool_calls = [i for i in response.output if i.type == "function_call"]
    if not tool_calls:
        break
    input += response.output
    for tc in tool_calls:
        result = registry[tc.name](**json.loads(tc.arguments))
        input.append({
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": result,
        })

print(response.output_text)
# -> call: lookup_customer(alice@example.com)
# -> result: CUS_8f3a2b
# -> call: get_balance(CUS_8f3a2b)
# -> result: $1,432.50
# "The balance for alice@example.com is $1,432.50."
