import anthropic

LLM_MODEL = "claude-opus-4-6"

client = anthropic.Anthropic()

ARTICLE = """\
BrightHome Inc. of Austin, Texas, has recalled 142,000 SmartHeat Pro
space heaters due to fire and burn hazards. The company received 23
reports of overheating, including 4 fires and 2 minor burn injuries.
No deaths have been reported. The heaters were sold at HomeBase,
WarmthPlus, and Amazon.com from September 2023 through February 2024
for between $89 and $149."""

# instead of output_format, use a tool call to extract data —
# the LLM "calls" the function, and we capture the arguments
tools = [{
    "name": "extract_recall",
    "description": "Extract product recall information from an article.",
    "input_schema": {
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

response = client.messages.create(
    model=LLM_MODEL,
    max_tokens=1024,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "Extract recall data from this article:\n\n" + ARTICLE,
    }],
)

# block.input is already a dict — no json.loads needed
tool_block = next(b for b in response.content if b.type == "tool_use")
print(tool_block.input)
# {'product': 'SmartHeat Pro', 'company': 'BrightHome Inc.', 'units_affected': 142000,
#  'hazard': 'fire and burn', 'injuries_reported': 2, 'fatalities': False,
#  'retailers': ['HomeBase', 'WarmthPlus', 'Amazon.com']}
