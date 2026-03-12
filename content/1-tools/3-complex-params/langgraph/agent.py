from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

# nested Pydantic models as type hints → JSON schema for the LLM
class LineItem(BaseModel):
    sku: str = Field(description="Product SKU, e.g. 'SKU_921'")
    quantity: int = Field(ge=1, description="Number of units to order")
    gift_wrap: bool = Field(default=False, description="Wrap item in gift packaging")

class ShippingAddress(BaseModel):
    street: str
    city: str
    zip: str = Field(description="Postal/ZIP code")
    country: str = Field(description="ISO 3166-1 alpha-2 country code, e.g. 'US'")

@tool
def place_order(
    items: list[LineItem],
    shipping: ShippingAddress,
    shipping_method: Literal["standard", "express", "overnight"] = "standard",
    notes: str | None = None,
) -> str:
    """Place an order with line items and shipping details."""
    print(f"-> call: place_order({len(items)} items, {shipping_method})")
    summary = ", ".join(
        f"{i.quantity}× {i.sku}" + (" (gift)" if i.gift_wrap else "")
        for i in items
    )
    result = (
        f"Order ORD_743 confirmed:\n"
        f"  {summary}.\n"
        f"  {shipping_method} to {shipping.city}."
    )
    print(f"-> result: {result}")
    return result

agent = create_agent(model, [place_order])
result = agent.invoke({
    "messages": [(
        "user",
        """\
        Order 2 of SKU_921 with gift wrap and 1 of SKU_114.
        Ship overnight to 100 Main St, San Francisco 94105, US.
        Leave at the back door.""",
    )],
})
print(result["messages"][-1].content)
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
