# equivalent raw tool schema — what to_tool() generates
# replaces: to_tool(), registry

tools = [
    {
        "name": "lookup_customer",
        "description": "Look up a customer by email and return their internal ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
            },
            "required": ["email"],
        },
    },
    {
        "name": "get_balance",
        "description": "Get the account balance for a customer ID",
        "input_schema": {
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
# result = fns[block.name](**block.input)
