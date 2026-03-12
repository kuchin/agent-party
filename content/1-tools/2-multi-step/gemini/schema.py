# equivalent raw tool schema — same contract the SDK derives from the function
# replaces: passing Python functions directly

from google.genai import types

tools = [types.Tool(function_declarations=[
    {
        "name": "lookup_customer",
        "description": "Look up a customer by email and return their internal ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
            },
            "required": ["email"],
        },
    },
    {
        "name": "get_balance",
        "description": "Get the account balance for a customer ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
            },
            "required": ["customer_id"],
        },
    },
])]

# with manual calling, dispatch tool calls yourself:
# fns = {"lookup_customer": lookup_customer, "get_balance": get_balance}
# result = fns[tool_call.name](**tool_call.args)
