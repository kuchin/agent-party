from typing import Literal
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)


class TicketAnalysis(BaseModel):
    category: Literal["billing", "technical", "account", "product"]
    priority: Literal["low", "medium", "high", "critical"]
    sentiment: Literal["positive", "neutral", "negative"]
    requires_escalation: bool
    summary: str = Field(description="One-sentence summary of the issue")
    suggested_tags: list[str] = Field(description="1-4 short labels for routing")


# response_format wires structured output through the agent API
agent = create_agent(model, tools=[], response_format=TicketAnalysis)

result = agent.invoke({
    "messages": [("user", """\
        Analyze this support ticket:
        'I've been charged twice for my Pro subscription this month.
        I contacted support 3 days ago and haven't heard back.
        If this isn't resolved by Friday I'm switching to a competitor.'""")]
})
print(result["structured_response"])
# category='billing' priority='high' sentiment='negative' requires_escalation=True
# summary='Customer was double-charged for Pro subscription and hasn't received support.'
# suggested_tags=['billing', 'double-charge', 'escalation', 'churn-risk']
