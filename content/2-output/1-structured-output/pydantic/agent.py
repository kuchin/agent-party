from typing import Literal
from pydantic import BaseModel, Field
from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"


class TicketAnalysis(BaseModel):
    category: Literal["billing", "technical", "account", "product"]
    priority: Literal["low", "medium", "high", "critical"]
    sentiment: Literal["positive", "neutral", "negative"]
    requires_escalation: bool
    summary: str = Field(description="One-sentence summary of the issue")
    suggested_tags: list[str] = Field(description="1-4 short labels for routing")


# output_type constrains the agent to return a validated TicketAnalysis
agent = Agent(LLM_MODEL, output_type=TicketAnalysis)

result = agent.run_sync("""\
    Analyze this support ticket:
    'I've been charged twice for my Pro subscription this month.
    I contacted support 3 days ago and haven't heard back.
    If this isn't resolved by Friday I'm switching to a competitor.'""")
print(result.output)
# category='billing' priority='high' sentiment='negative' requires_escalation=True
# summary='Customer was double-charged for Pro subscription and hasn't received support.'
# suggested_tags=['billing', 'double-charge', 'escalation', 'churn-risk']
