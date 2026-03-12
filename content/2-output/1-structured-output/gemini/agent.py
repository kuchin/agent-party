from typing import Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()


class TicketAnalysis(BaseModel):
    category: Literal["billing", "technical", "account", "product"]
    priority: Literal["low", "medium", "high", "critical"]
    sentiment: Literal["positive", "neutral", "negative"]
    requires_escalation: bool
    summary: str = Field(description="One-sentence summary of the issue")
    suggested_tags: list[str] = Field(description="1-4 short labels for routing")


# response_schema accepts a Pydantic class; response_mime_type forces JSON output
config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=TicketAnalysis,
)

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents="""\
        Analyze this support ticket:
        'I've been charged twice for my Pro subscription this month.
        I contacted support 3 days ago and haven't heard back.
        If this isn't resolved by Friday I'm switching to a competitor.'""",
)
print(response.parsed)
# category='billing' priority='high' sentiment='negative' requires_escalation=True
# summary='Customer was double-charged for Pro subscription and hasn't received support.'
# suggested_tags=['billing', 'double-charge', 'escalation', 'churn-risk']
