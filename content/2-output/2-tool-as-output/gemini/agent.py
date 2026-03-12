from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()

ARTICLE = """\
BrightHome Inc. of Austin, Texas, has recalled 142,000 SmartHeat Pro
space heaters due to fire and burn hazards. The company received 23
reports of overheating, including 4 fires and 2 minor burn injuries.
No deaths have been reported. The heaters were sold at HomeBase,
WarmthPlus, and Amazon.com from September 2023 through February 2024
for between $89 and $149."""

# instead of response_schema, use a tool call to extract data —
# the LLM "calls" the function, and we capture the arguments
tools = [types.Tool(function_declarations=[{
    "name": "extract_recall",
    "description": "Extract product recall information from an article.",
    "parameters": {
        "type": "object",
        "properties": {
            "product": {"type": "string"},
            "company": {"type": "string"},
            "units_affected": {"type": "integer"},
            "hazard": {"type": "string", "description": "Primary hazard"},
            "injuries_reported": {"type": "integer"},
            "fatalities": {"type": "boolean"},
            "retailers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Stores that sold the product",
            },
        },
        "required": [
            "product", "company", "units_affected", "hazard",
            "injuries_reported", "fatalities", "retailers",
        ],
    },
}])]

config = types.GenerateContentConfig(tools=tools)

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents="Extract recall data from this article:\n\n" + ARTICLE,
)

tool_call = response.function_calls[0]
print(dict(tool_call.args))
# {'product': 'SmartHeat Pro', 'company': 'BrightHome Inc.', 'units_affected': 142000,
#  'hazard': 'fire and burn', 'injuries_reported': 2, 'fatalities': False,
#  'retailers': ['HomeBase', 'WarmthPlus', 'Amazon.com']}
