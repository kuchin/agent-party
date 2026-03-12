from typing import Literal
import anthropic
from pydantic import BaseModel, Field

LLM_MODEL = "claude-opus-4-6"

client = anthropic.Anthropic()


# nested Pydantic models → rich JSON schema for the LLM
class LineItem(BaseModel):
    sku: str = Field(description="Product SKU, e.g. 'SKU_921'")
    quantity: int = Field(ge=1, description="Number of units to order")
    gift_wrap: bool = Field(default=False, description="Wrap item in gift packaging")

class ShippingAddress(BaseModel):
    street: str
    city: str
    zip: str = Field(description="Postal/ZIP code")
    country: str = Field(description="ISO 3166-1 alpha-2 country code, e.g. 'US'")

class PlaceOrderParams(BaseModel):
    items: list[LineItem]
    shipping: ShippingAddress
    shipping_method: Literal["standard", "express", "overnight"] = "standard"
    notes: str | None = Field(default=None, description="Delivery instructions")


# block.input is already a dict — wrapping in PlaceOrderParams
# gives us validated, typed access (params.items[0].sku vs params['items'][0]['sku'])
def place_order(params: PlaceOrderParams) -> str:
    """Place an order with line items and shipping details."""
    print(f"-> call: place_order({len(params.items)} items, {params.shipping_method})")
    summary = ", ".join(
        f"{i.quantity}× {i.sku}" + (" (gift)" if i.gift_wrap else "")
        for i in params.items
    )
    result = (
        f"Order ORD_743 confirmed:\n"
        f"  {summary}.\n"
        f"  {params.shipping_method} to {params.shipping.city}."
    )
    print(f"-> result: {result}")
    return result


# build tool schema and register for dispatch
registry = {}

def to_tool(fn, params_model):
    registry[fn.__name__] = (fn, params_model)
    return {
        "name": fn.__name__,
        "description": fn.__doc__,
        "input_schema": params_model.model_json_schema(),
    }

tools = [to_tool(place_order, PlaceOrderParams)]

messages = [{"role": "user", "content": """\
    Order 2 of SKU_921 with gift wrap and 1 of SKU_114.
    Ship overnight to 100 Main St, San Francisco 94105, US.
    Leave at the back door.""",
}]

# ReAct loop: LLM calls tools until it can answer
while True:
    response = client.messages.create(
        model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
    )
    if response.stop_reason != "tool_use":
        break
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            fn, params_model = registry[block.name]
            result = fn(params_model(**block.input))
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
    messages.append({"role": "user", "content": tool_results})

print(response.content[0].text)
# -> call: place_order(2 items, overnight)
# -> result: Order ORD_743 confirmed:
#   2× SKU_921 (gift), 1× SKU_114.
#   overnight to San Francisco.
# "Done - order ORD_743 is confirmed.
# - 2 × SKU_921, gift wrapped
# - 1 × SKU_114
# - Shipping: overnight
# - Address: 100 Main St, San Francisco, 94105, US
# - Note: Leave at the back door."
