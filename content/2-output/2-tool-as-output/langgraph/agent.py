from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

ARTICLE = """\
BrightHome Inc. of Austin, Texas, has recalled 142,000 SmartHeat Pro
space heaters due to fire and burn hazards. The company received 23
reports of overheating, including 4 fires and 2 minor burn injuries.
No deaths have been reported. The heaters were sold at HomeBase,
WarmthPlus, and Amazon.com from September 2023 through February 2024
for between $89 and $149."""


# instead of with_structured_output(), use a tool call to extract data —
# the LLM "calls" the tool, and we capture the arguments
class RecallData(BaseModel):
    """Extract product recall information from an article."""
    product: str
    company: str
    units_affected: int
    hazard: str = Field(description="Primary hazard")
    injuries_reported: int
    fatalities: bool
    retailers: list[str] = Field(description="Stores that sold the product")


# tool-as-output needs the tool call arguments without executing the tool,
# so this example binds the schema on the chat model instead of using an agent
model_with_tools = model.bind_tools([RecallData])

response = model_with_tools.invoke(
    "Extract recall data from this article:\n\n" + ARTICLE
)
print(response.tool_calls[0]["args"])
# {'product': 'SmartHeat Pro', 'company': 'BrightHome Inc.', 'units_affected': 142000,
#  'hazard': 'fire and burn', 'injuries_reported': 2, 'fatalities': False,
#  'retailers': ['HomeBase', 'WarmthPlus', 'Amazon.com']}
