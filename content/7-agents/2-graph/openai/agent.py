from typing import Literal
from pydantic import BaseModel, Field
from openai import OpenAI

LLM_MODEL = "gpt-5.4"

client = OpenAI()

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


# --- Structured output schemas ---
# The LLM returns typed data at two pipeline steps:
# 1. Classification — claim type and estimated cost
# 2. Extraction — specific fields that vary by claim category

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


# --- LLM-powered steps ---
# Each function makes one LLM call with structured output.
# The system prompt defines the task; the schema constrains the response.

def classify_claim(claim_text: str) -> ClaimClassification:
    """Classify the claim type and estimate the amount."""
    response = client.responses.parse(
        model=LLM_MODEL,
        text_format=ClaimClassification,
        input=[
            {"role": "system", "content": """\
You are an insurance claim classifier. Determine:
1. category: "auto" for vehicle claims, "home" for property claims
2. estimated_amount: dollar estimate based on the damage described"""},
            {"role": "user", "content": claim_text},
        ],
    )
    return response.output_parsed

def extract_auto(claim_text: str, retry_hint: str = "") -> AutoExtraction:
    """Extract vehicle-specific fields from the claim text."""
    prompt = claim_text
    if retry_hint:
        prompt += f"\n\nPrevious extraction was missing: {retry_hint}. Look carefully."
    response = client.responses.parse(
        model=LLM_MODEL,
        text_format=AutoExtraction,
        input=[
            {"role": "system", "content": """\
Extract structured details from this auto insurance claim.
Return null for optional fields not mentioned in the text."""},
            {"role": "user", "content": prompt},
        ],
    )
    return response.output_parsed

def extract_home(claim_text: str, retry_hint: str = "") -> HomeExtraction:
    """Extract property-specific fields from the claim text."""
    prompt = claim_text
    if retry_hint:
        prompt += f"\n\nPrevious extraction was missing: {retry_hint}. Look carefully."
    response = client.responses.parse(
        model=LLM_MODEL,
        text_format=HomeExtraction,
        input=[
            {"role": "system", "content": """\
Extract structured details from this home insurance claim.
Return null for optional fields not mentioned in the text."""},
            {"role": "user", "content": prompt},
        ],
    )
    return response.output_parsed


# --- Deterministic steps (plain code, not LLM) ---
# Business rules that must be exact, auditable, and reproducible.

def check_fraud(customer_id: str) -> dict:
    """Score fraud risk from claim history."""
    history = FRAUD_HISTORY.get(customer_id, {"claims_12mo": 0, "fraud_flags": 0})
    score = history["claims_12mo"] * 10 + history["fraud_flags"] * 30
    return {"fraud_score": score, "flagged": score > 50}

def validate_extraction(extraction: dict, category: str) -> list[str]:
    """Check required fields have values. Returns missing field names."""
    required = {
        "auto": ["vehicles", "damage"],
        "home": ["damage_type", "rooms"],
    }
    return [f for f in required.get(category, []) if not extraction.get(f)]

def decide(category: str, amount: int, customer: dict) -> dict:
    """Apply coverage rules to reach approve / review / deny."""
    policy = COVERAGE[customer["policy_type"]]
    if category not in policy["covered_types"]:
        return {"decision": "deny", "reason": "Not covered under policy"}
    if amount <= 1000:
        return {"decision": "approve", "reason": "Under auto-approval threshold"}
    return {"decision": "review", "reason": "Amount exceeds auto-approval, adjuster required"}


# --- Pipeline orchestration ---
# No graph abstraction — the pipeline IS the code. Branching is if/else,
# retry is a for loop, parallel could be asyncio.gather (kept sequential here).
# This is shorter than a graph definition, but you lose visual debugging,
# state snapshots, and the ability to test nodes independently.
# See flow.txt for the visual diagram of what this code implements.

# step 1: classify + fraud check (independent — could run in parallel)
classification = classify_claim(CLAIM_TEXT)
fraud = check_fraud(CUSTOMER["id"])
print(f"Classify: {classification.category}, ${classification.estimated_amount}")
print(f"Fraud:    score={fraud['fraud_score']}, flagged={fraud['flagged']}")

# step 2: fraud gate — reject immediately if flagged
if fraud["flagged"]:
    print("\nREJECTED — fraud risk too high")
    exit()

# step 3: extract details based on claim category (with retry for missing fields)
# auto claims need vehicle/damage/police info; home claims need damage type/rooms/estimate
retry_hint = ""
for attempt in range(3):  # 1 initial + up to 2 retries
    if classification.category == "auto":
        extraction = extract_auto(CLAIM_TEXT, retry_hint).model_dump()
    else:
        extraction = extract_home(CLAIM_TEXT, retry_hint).model_dump()

    missing = validate_extraction(extraction, classification.category)
    if not missing:
        break
    retry_hint = ", ".join(missing)
    print(f"Retry {attempt + 1}/2: missing {missing}")
else:
    print("\nFAILED — extraction incomplete after retries")
    exit()

print(f"Extract:  {extraction}")

# step 4: decide
result = decide(classification.category, classification.estimated_amount, CUSTOMER)
print(f"\nDecision: {result['decision'].upper()}")
print(f"Reason:   {result['reason']}")
# Classify: auto, $5000
# Fraud:    score=10, flagged=False
# Extract:  {'vehicles': '2022 Honda Civic', 'damage': 'rear bumper and trunk...', 'police_report': '2025-MP-00481'}
# Decision: REVIEW
# Reason:   Amount exceeds auto-approval, adjuster required
