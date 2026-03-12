# equivalent raw tool schema — what to_tool() + Pydantic generates
# replaces: LineItem, ShippingAddress, PlaceOrderParams, to_tool(), registry

tools = [
    {
        "type": "function",
        "name": "place_order",
        "description": "Place an order with line items and shipping details",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sku": {
                                "type": "string",
                                "description": "Product SKU, e.g. 'SKU_921'",
                            },
                            "quantity": {
                                "type": "integer",
                                "minimum": 1,
                                "description": "Number of units to order",
                            },
                            "gift_wrap": {
                                "type": "boolean",
                                "default": False,
                                "description": "Wrap item in gift packaging",
                            },
                        },
                        "required": ["sku", "quantity"],
                    },
                },
                "shipping": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "zip": {
                            "type": "string",
                            "description": "Postal/ZIP code",
                        },
                        "country": {
                            "type": "string",
                            "description": "ISO 3166-1 alpha-2 country code, e.g. 'US'",
                        },
                    },
                    "required": ["street", "city", "zip", "country"],
                },
                "shipping_method": {
                    "type": "string",
                    "enum": ["standard", "express", "overnight"],
                    "default": "standard",
                },
                "notes": {
                    "type": "string",
                    "description": "Delivery instructions",
                },
            },
            "required": ["items", "shipping"],
        },
    },
]

# dispatch tool calls manually:
# result = place_order(**json.loads(tool_call.arguments))
