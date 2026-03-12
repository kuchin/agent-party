from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"

agent = Agent(LLM_MODEL)

ARTICLE = """\
BrightHome Inc. of Austin, Texas, has recalled 142,000 SmartHeat Pro
space heaters due to fire and burn hazards. The company received 23
reports of overheating, including 4 fires and 2 minor burn injuries.
No deaths have been reported. The heaters were sold at HomeBase,
WarmthPlus, and Amazon.com from September 2023 through February 2024
for between $89 and $149."""

# instead of output_type, use a tool call to extract data —
# the LLM "calls" the function, and we capture the arguments

@agent.tool_plain
def extract_recall(
    product: str, company: str, units_affected: int,
    hazard: str, injuries_reported: int, fatalities: bool,
    retailers: list[str],
) -> str:
    """Extract product recall information from an article."""
    print({
        "product": product, "company": company,
        "units_affected": units_affected, "hazard": hazard,
        "injuries_reported": injuries_reported, "fatalities": fatalities,
        "retailers": retailers,
    })
    return "Extracted."

result = agent.run_sync(
    "Extract recall data from this article:\n\n" + ARTICLE
)
# {'product': 'SmartHeat Pro', 'company': 'BrightHome Inc.', 'units_affected': 142000,
#  'hazard': 'fire and burn', 'injuries_reported': 2, 'fatalities': False,
#  'retailers': ['HomeBase', 'WarmthPlus', 'Amazon.com']}
