# equivalent hand-written tool schema for Anthropic's input_schema
# same contract as PlaceOrderParams, flattened for readability

tools = [
    {
        "name": "place_order",
        "description": "Place an order with line items and shipping details",
        "input_schema": {
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

# dispatch tool calls with the typed params model:
# block = next(b for b in response.content if b.type == "tool_use")
# result = place_order(PlaceOrderParams(**block.input))
