# equivalent raw tool schema — same contract the SDK derives from the Pydantic model
# replaces: FunctionDeclaration, parameters_json_schema, Pydantic models

from google.genai import types

tools = [types.Tool(function_declarations=[{
    "name": "place_order",
    "description": "Place an order with line items and shipping details.",
    "parameters": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sku": {"type": "string", "description": "Product SKU"},
                        "quantity": {"type": "integer", "minimum": 1},
                        "gift_wrap": {"type": "boolean"},
                    },
                    "required": ["sku", "quantity"],
                },
            },
            "shipping": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zip": {"type": "string"},
                    "country": {"type": "string"},
                },
                "required": ["street", "city", "zip", "country"],
            },
            "shipping_method": {
                "type": "string",
                "enum": ["standard", "express", "overnight"],
            },
            "notes": {"type": "string"},
        },
        "required": ["items", "shipping"],
    },
}])]

# dispatch tool calls manually:
# result = place_order(PlaceOrderParams(**tool_call.args))
