from typing import Literal
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()


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


tools = [types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="place_order",
        description=place_order.__doc__,
        parameters_json_schema=PlaceOrderParams.model_json_schema(),
    ),
])]

config = types.GenerateContentConfig(tools=tools)

contents = [
    types.Content(role="user", parts=[types.Part.from_text(text="""\
        Order 2 of SKU_921 with gift wrap and 1 of SKU_114.
        Ship overnight to 100 Main St, San Francisco 94105, US.
        Leave at the back door.""",
    )]),
]

# ReAct loop: LLM calls tools until it can answer
while True:
    response = client.models.generate_content(
        model=LLM_MODEL, config=config, contents=contents,
    )
    if not response.function_calls:
        break
    contents.append(response.candidates[0].content)
    for tool_call in response.function_calls:
        result = place_order(PlaceOrderParams(**tool_call.args))
        contents.append(types.Content(role="tool", parts=[
            types.Part.from_function_response(
                name=tool_call.name,
                response={"result": result},
            ),
        ]))

print(response.text)
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
