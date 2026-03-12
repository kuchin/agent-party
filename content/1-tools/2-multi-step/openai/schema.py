# equivalent raw tool schema — what to_tool() + Pydantic generates
# replaces: LookupCustomerParams, GetBalanceParams, to_tool(), registry

tools = [
    {
        "type": "function",
        "name": "lookup_customer",
        "description": "Look up a customer by email and return their internal ID",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
            },
            "required": ["email"],
        },
    },
    {
        "type": "function",
        "name": "get_balance",
        "description": "Get the account balance for a customer ID",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
            },
            "required": ["customer_id"],
        },
    },
]

# dispatch tool calls manually:
# fns = {"lookup_customer": lookup_customer, "get_balance": get_balance}
# result = fns[tc.name](**json.loads(tc.arguments))
