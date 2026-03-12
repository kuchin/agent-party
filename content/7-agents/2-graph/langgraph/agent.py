import warnings
from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# langchain-openai's internal model_dump() triggers a Pydantic serialization
# warning when with_structured_output() returns a parsed BaseModel instance.
# The output is correct — this suppresses the cosmetic noise.
warnings.filterwarnings("ignore", message=".*PydanticSerializationUnexpectedValue.*")

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

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

# fraud check uses claim history — in production, query a risk database
FRAUD_HISTORY = {
    "C-1234": {"claims_12mo": 1, "fraud_flags": 0},  # low risk
}

# coverage rules by policy type
COVERAGE = {
    "auto-premium": {"covered_types": ["auto"], "limit": 50_000, "deductible": 500},
    "home-basic":   {"covered_types": ["home"], "limit": 25_000, "deductible": 1_000},
}


# --- Pipeline state ---
# Everything the pipeline needs to track flows through this single state object.
# Each node reads what it needs and returns a partial update.

class ClaimState(TypedDict, total=False):
    claim_text: str
    customer_id: str
    category: str
    estimated_amount: int
    fraud_score: int
    flagged: bool
    extraction: dict
    missing_fields: list[str]
    retries: int
    decision: str
    reason: str


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


# --- Graph nodes ---
# Each node is a function: takes the full state, returns a partial state update.
# with_structured_output binds a Pydantic schema to the model for typed responses.

def classify_node(state: ClaimState) -> dict:
    """LLM node: classify the claim type and estimate amount."""
    structured = model.with_structured_output(ClaimClassification)
    result = structured.invoke([
        ("system", """\
You are an insurance claim classifier. Determine:
1. category: "auto" for vehicle claims, "home" for property claims
2. estimated_amount: dollar estimate based on the damage described"""),
        ("user", state["claim_text"]),
    ])
    print(f"Classify: {result.category}, ${result.estimated_amount}")
    return {"category": result.category, "estimated_amount": result.estimated_amount}

def fraud_check_node(state: ClaimState) -> dict:
    """Deterministic node: score fraud risk from claim history."""
    history = FRAUD_HISTORY.get(state["customer_id"], {"claims_12mo": 0, "fraud_flags": 0})
    score = history["claims_12mo"] * 10 + history["fraud_flags"] * 30
    flagged = score > 50
    print(f"Fraud:    score={score}, flagged={flagged}")
    return {"fraud_score": score, "flagged": flagged}

def extract_node(state: ClaimState) -> dict:
    """LLM node: extract claim details based on category."""
    schema = AutoExtraction if state["category"] == "auto" else HomeExtraction
    structured = model.with_structured_output(schema)
    prompt = state["claim_text"]
    if state.get("missing_fields"):
        prompt += f"\n\nPrevious extraction was missing: {', '.join(state['missing_fields'])}. Look carefully."
    result = structured.invoke([
        ("system", """\
Extract structured details from this insurance claim.
Return null for optional fields not mentioned in the text."""),
        ("user", prompt),
    ])
    retries = state.get("retries", 0) + 1
    print(f"Extract:  {result.model_dump()} (attempt {retries})")
    return {"extraction": result.model_dump(), "retries": retries}

def validate_node(state: ClaimState) -> dict:
    """Deterministic node: check required fields are present."""
    required = {"auto": ["vehicles", "damage"], "home": ["damage_type", "rooms"]}
    missing = [f for f in required.get(state["category"], []) if not state["extraction"].get(f)]
    if missing:
        print(f"Validate: missing {missing}")
    return {"missing_fields": missing}

def decide_node(state: ClaimState) -> dict:
    """Deterministic node: apply coverage rules."""
    policy = COVERAGE[CUSTOMER["policy_type"]]
    if state["category"] not in policy["covered_types"]:
        result = {"decision": "deny", "reason": "Not covered under policy"}
    elif state["estimated_amount"] <= 1000:
        result = {"decision": "approve", "reason": "Under auto-approval threshold"}
    else:
        result = {"decision": "review", "reason": "Amount exceeds auto-approval, adjuster required"}
    print(f"\nDecision: {result['decision'].upper()}")
    print(f"Reason:   {result['reason']}")
    return result


# --- Graph definition ---
# The graph IS the orchestration. Nodes are steps, edges define flow.
# Compare this with the raw SDK version (OpenAI/Anthropic) where if/else IS the flow.
# The graph gives you: visual debugging, state snapshots, independent node testing.
# See flow.txt for the visual diagram this graph implements.

graph = StateGraph(ClaimState)

graph.add_node("classify", classify_node)
graph.add_node("fraud_check", fraud_check_node)
# routing-only node: synchronization point after parallel classify + fraud check
graph.add_node("fraud_gate", lambda state: {})
graph.add_node("extract", extract_node)
graph.add_node("validate", validate_node)
graph.add_node("decide", decide_node)

# step 1: classify + fraud check run in parallel from START
graph.add_edge(START, "classify")
graph.add_edge(START, "fraud_check")

# fan-in: both must complete before the fraud gate runs
graph.add_edge("classify", "fraud_gate")
graph.add_edge("fraud_check", "fraud_gate")

# step 2: fraud gate — reject if flagged, otherwise extract
graph.add_conditional_edges("fraud_gate",
    lambda s: END if s.get("flagged") else "extract",
)

# step 3 → 4: extract then validate
graph.add_edge("extract", "validate")

# step 4: validate — retry extract if fields missing (max 3 attempts), else decide
graph.add_conditional_edges("validate",
    lambda s: "extract" if s.get("missing_fields") and s.get("retries", 0) < 3 else "decide",
)

# step 5: decide → done
graph.add_edge("decide", END)

# --- Run ---
app = graph.compile()
result = app.invoke({
    "claim_text": CLAIM_TEXT,
    "customer_id": CUSTOMER["id"],
})
# Classify: auto, $5000
# Fraud:    score=10, flagged=False
# Extract:  {'vehicles': '2022 Honda Civic', 'damage': 'rear bumper and trunk...', ...} (attempt 1)
# Decision: REVIEW
# Reason:   Amount exceeds auto-approval, adjuster required
