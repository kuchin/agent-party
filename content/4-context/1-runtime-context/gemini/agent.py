from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# mock database — in production these are real queries
ORDERS = {
    "user_123": [
        {"id": "ORD_99", "item": "Laptop Stand", "status": "shipped"},
        {"id": "ORD_100", "item": "USB Hub", "status": "processing"},
    ],
}

# status is chosen by the LLM — user_id comes from your app (auth, session, etc.)
# only status appears in the tool schema — the LLM can't see or fabricate user_id
user_id = "user_123"

def get_orders(status: str) -> str:
    """Get orders filtered by status."""
    print(f"-> call: get_orders({status}) for {user_id}")
    matches = [o for o in ORDERS[user_id] if o["status"] == status]
    result = ", ".join(f'{o["id"]}: {o["item"]}' for o in matches) or "No orders found."
    print(f"-> result: {result}")
    return result

# automatic function calling: SDK executes the tool and feeds results back
config = types.GenerateContentConfig(tools=[get_orders])

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents="Do I have any shipped orders?",
)
print(response.text)
# -> call: get_orders(shipped) for user_123
# -> result: ORD_99: Laptop Stand
# "Your shipped order is ORD_99: Laptop Stand."
