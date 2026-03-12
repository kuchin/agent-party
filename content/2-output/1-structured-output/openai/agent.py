from typing import Literal
from pydantic import BaseModel, Field
from openai import OpenAI

LLM_MODEL = "gpt-5.4"

client = OpenAI()


class TicketAnalysis(BaseModel):
    category: Literal["billing", "technical", "account", "product"]
    priority: Literal["low", "medium", "high", "critical"]
    sentiment: Literal["positive", "neutral", "negative"]
    requires_escalation: bool
    summary: str = Field(description="One-sentence summary of the issue")
    suggested_tags: list[str] = Field(description="1-4 short labels for routing")


# text_format enforces the Pydantic schema on the LLM response
response = client.responses.parse(
    model=LLM_MODEL,
    text_format=TicketAnalysis,
    input=[{
        "role": "user",
        "content": """\
            Analyze this support ticket:
            'I've been charged twice for my Pro subscription this month.
            I contacted support 3 days ago and haven't heard back.
            If this isn't resolved by Friday I'm switching to a competitor.'""",
    }],
)
print(response.output_parsed)
# category='billing' priority='high' sentiment='negative' requires_escalation=True
# summary='Customer was double-charged for Pro subscription and hasn't received support.'
# suggested_tags=['billing', 'double-charge', 'escalation', 'churn-risk']
