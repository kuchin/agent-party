import json
from openai import OpenAI

LLM_MODEL = "gpt-5.4"

client = OpenAI()

ARTICLE = """\
BrightHome Inc. of Austin, Texas, has recalled 142,000 SmartHeat Pro
space heaters due to fire and burn hazards. The company received 23
reports of overheating, including 4 fires and 2 minor burn injuries.
No deaths have been reported. The heaters were sold at HomeBase,
WarmthPlus, and Amazon.com from September 2023 through February 2024
for between $89 and $149."""

# instead of text_format, use a tool call to extract data —
# the LLM "calls" the function, and we capture the arguments
tools = [{
    "type": "function",
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
}]

response = client.responses.create(
    model=LLM_MODEL,
    tools=tools,
    input=[{
        "role": "user",
        "content": "Extract recall data from this article:\n\n" + ARTICLE,
    }],
)

tool_call = next(i for i in response.output if i.type == "function_call")
print(json.loads(tool_call.arguments))
# {'product': 'SmartHeat Pro', 'company': 'BrightHome Inc.', 'units_affected': 142000,
#  'hazard': 'fire and burn', 'injuries_reported': 2, 'fatalities': False,
#  'retailers': ['HomeBase', 'WarmthPlus', 'Amazon.com']}
