from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_graph.beta import GraphBuilder, StepContext
from pydantic_graph.beta.join import reduce_dict_update

LLM_MODEL = "openai:gpt-5.4"

# --- Mock data ---
# In production these come from the customer portal, policy database, and risk engine.

CLAIM_TEXT = """\
I was in a car accident on Highway 101 on March 3rd. Another vehicle \
rear-ended me at a stoplight. My rear bumper and trunk are badly damaged. \
The other driver has State Farm, policy SF-443892. My car is a 2022 \
Honda Civic. Officer gave me case number 2025-MP-00481."""

CUSTOMER = {
    "id": "C-1234",
    "policy_type": "auto-premium",
    "coverage_limit": 50_000,
    "deductible": 500,
}

FRAUD_HISTORY = {
    "C-1234": {"claims_12mo": 1, "fraud_flags": 0},
}

COVERAGE = {
    "auto-premium": {"covered_types": ["auto"], "limit": 50_000, "deductible": 500},
    "home-basic":   {"covered_types": ["home"], "limit": 25_000, "deductible": 1_000},
}


# --- Pipeline state ---
# A dataclass that flows through the entire graph.
# Each step reads what it needs from state and mutates the relevant fields.

@dataclass
class ClaimState:
    claim_text: str = ""
    customer_id: str = ""
    category: str = ""
    estimated_amount: int = 0
    fraud_score: int = 0
    flagged: bool = False
    extraction: dict = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    retries: int = 0


# --- Structured output schemas ---

class ClaimClassification(BaseModel):
    category: Literal["auto", "home"]
    estimated_amount: int = Field(description="Estimated claim amount in dollars")

class AutoExtraction(BaseModel):
    vehicles: str = Field(description="Vehicles involved in the incident")
    damage: str = Field(description="Description of damage")
    police_report: str | None = Field(description="Police report number if mentioned")

class HomeExtraction(BaseModel):
    damage_type: str = Field(description="Type of home damage (fire, water, etc.)")
    rooms: str = Field(description="Affected rooms or areas")
    contractor_estimate: int | None = Field(description="Contractor estimate if mentioned")


# --- Agents for structured LLM output ---
# Each agent wraps a single LLM call with a typed response schema.

classify_agent = Agent(LLM_MODEL,
    output_type=ClaimClassification,
    system_prompt="""\
You are an insurance claim classifier. Determine:
1. category: "auto" for vehicle claims, "home" for property claims
2. estimated_amount: dollar estimate based on the damage described""",
)

extract_auto_agent = Agent(LLM_MODEL,
    output_type=AutoExtraction,
    system_prompt="""\
Extract structured details from this auto insurance claim.
Return null for optional fields not mentioned in the text.""",
)

extract_home_agent = Agent(LLM_MODEL,
    output_type=HomeExtraction,
    system_prompt="""\
Extract structured details from this home insurance claim.
Return null for optional fields not mentioned in the text.""",
)


# --- Graph definition (beta GraphBuilder API) ---
# The beta API supports parallel execution via broadcast/join — the stable
# BaseNode API only supports sequential graphs. Steps are async functions
# decorated with @g.step. Data flows through ctx.state (shared mutable state)
# and ctx.inputs (output from the previous step).
# See flow.txt for the visual diagram this graph implements.

g = GraphBuilder(state_type=ClaimState, input_type=str, output_type=dict)


# step 1a: classify the claim (LLM) — runs in parallel with fraud check
@g.step
async def classify(ctx: StepContext[ClaimState, None, str]) -> dict:
    """LLM step: classify the claim type and estimate amount."""
    result = await classify_agent.run(ctx.state.claim_text)
    ctx.state.category = result.output.category
    ctx.state.estimated_amount = result.output.estimated_amount
    print(f"Classify: {ctx.state.category}, ${ctx.state.estimated_amount}")
    return {"category": ctx.state.category, "amount": ctx.state.estimated_amount}


# step 1b: check fraud (deterministic) — runs in parallel with classify
@g.step
async def fraud_check(ctx: StepContext[ClaimState, None, str]) -> dict:
    """Deterministic step: score fraud risk from customer history."""
    history = FRAUD_HISTORY.get(ctx.state.customer_id, {"claims_12mo": 0, "fraud_flags": 0})
    ctx.state.fraud_score = history["claims_12mo"] * 10 + history["fraud_flags"] * 30
    ctx.state.flagged = ctx.state.fraud_score > 50
    print(f"Fraud:    score={ctx.state.fraud_score}, flagged={ctx.state.flagged}")
    return {"fraud_score": ctx.state.fraud_score, "flagged": ctx.state.flagged}


# join: merge parallel results into a single dict before the fraud gate.
# reduce_dict_update merges: {"category": ..., "amount": ...} + {"fraud_score": ..., "flagged": ...}
collect = g.join(reduce_dict_update, initial_factory=dict)


# step 2: fraud gate — reject early if fraud is flagged
@g.step
async def fraud_gate(ctx: StepContext[ClaimState, None, dict]) -> dict:
    """Gate step: reject the claim if fraud risk is too high."""
    if ctx.state.flagged:
        print("\nREJECTED — fraud risk too high")
        return {"decision": "reject", "reason": "Fraud risk too high"}
    return {"continue": True}


# step 3+4: extract details and validate (with retry loop)
# Handles category branching internally — auto vs home need different schemas.
@g.step
async def extract(ctx: StepContext[ClaimState, None, dict]) -> dict:
    """LLM step: extract claim details, retrying if required fields are missing."""
    agent = extract_auto_agent if ctx.state.category == "auto" else extract_home_agent
    required = ["vehicles", "damage"] if ctx.state.category == "auto" else ["damage_type", "rooms"]

    # extract with retry for missing fields (1 initial + up to 2 retries)
    for attempt in range(3):
        prompt = ctx.state.claim_text
        if ctx.state.missing_fields:
            prompt += f"\n\nPrevious extraction was missing: {', '.join(ctx.state.missing_fields)}. Look carefully."
        result = await agent.run(prompt)
        ctx.state.extraction = result.output.model_dump()
        ctx.state.retries += 1
        ctx.state.missing_fields = [f for f in required if not ctx.state.extraction.get(f)]
        if not ctx.state.missing_fields:
            break
        print(f"Retry {attempt + 1}/2: missing {ctx.state.missing_fields}")

    print(f"Extract:  {ctx.state.extraction} (attempt {ctx.state.retries})")
    return ctx.state.extraction


# step 5: apply coverage rules (deterministic)
@g.step
async def decide(ctx: StepContext[ClaimState, None, dict]) -> dict:
    """Deterministic step: apply coverage rules to produce final decision."""
    policy = COVERAGE[CUSTOMER["policy_type"]]
    if ctx.state.category not in policy["covered_types"]:
        result = {"decision": "deny", "reason": "Not covered under policy"}
    elif ctx.state.estimated_amount <= 1000:
        result = {"decision": "approve", "reason": "Under auto-approval threshold"}
    else:
        result = {"decision": "review", "reason": "Amount exceeds auto-approval, adjuster required"}
    print(f"\nDecision: {result['decision'].upper()}")
    print(f"Reason:   {result['reason']}")
    return result


# --- Wire the graph ---
# Edges define the flow. broadcast sends the same input to parallel steps;
# join merges their outputs via a reducer. Compare with LangGraph's explicit
# add_edge/add_conditional_edges — here the structure is built with
# edge_from/to chains and the type checker still validates step signatures.

g.add(
    # step 1: classify + fraud check run in parallel (broadcast from start)
    g.edge_from(g.start_node).to(classify, fraud_check),
    # join: merge parallel results into a single dict
    g.edge_from(classify, fraud_check).to(collect),
    # step 2: fraud gate — reject if flagged
    g.edge_from(collect).to(fraud_gate),
    # steps 3-5: extract → decide → end
    g.edge_from(fraud_gate).to(extract),
    g.edge_from(extract).to(decide),
    g.edge_from(decide).to(g.end_node),
)

graph = g.build()


# --- Run ---

async def main():
    state = ClaimState(claim_text=CLAIM_TEXT, customer_id=CUSTOMER["id"])
    result = await graph.run(state=state, inputs=CLAIM_TEXT)
    print(result)

asyncio.run(main())
# Classify: auto, $5000
# Fraud:    score=10, flagged=False
# Extract:  {'vehicles': '2022 Honda Civic', 'damage': 'rear bumper and trunk...', ...} (attempt 1)
# Decision: REVIEW
# Reason:   Amount exceeds auto-approval, adjuster required
# {'decision': 'review', 'reason': 'Amount exceeds auto-approval, adjuster required'}
