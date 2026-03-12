import json
from typing import Literal
from openai import OpenAI
from pydantic import BaseModel, Field

LLM_MODEL = "gpt-5.4"

client = OpenAI()


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


# json.loads returns raw dicts — wrapping in PlaceOrderParams
# gives us validated, typed access (params.items[0].sku vs i['sku'])
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
        "type": "function",
        "name": fn.__name__,
        "description": fn.__doc__,
        "parameters": params_model.model_json_schema(),
    }

tools = [to_tool(place_order, PlaceOrderParams)]

messages = [{
    "role": "user",
    "content": """\
        Order 2 of SKU_921 with gift wrap and 1 of SKU_114.
        Ship overnight to 100 Main St, San Francisco 94105, US.
        Leave at the back door.""",
}]

# ReAct loop: LLM calls tools until it can answer
while True:
    response = client.responses.create(
        model=LLM_MODEL, input=messages, tools=tools,
    )
    tool_calls = [i for i in response.output if i.type == "function_call"]
    if not tool_calls:
        break
    messages += response.output
    for tc in tool_calls:
        fn, params_model = registry[tc.name]
        result = fn(params_model(**json.loads(tc.arguments)))
        messages.append({
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": result,
        })

print(response.output_text)
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
