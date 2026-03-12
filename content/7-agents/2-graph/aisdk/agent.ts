import { generateText, Output } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

// --- Mock data ---
// In production these come from the customer portal, policy database, and risk engine.

const CLAIM_TEXT = `\
I was in a car accident on Highway 101 on March 3rd. Another vehicle \
rear-ended me at a stoplight. My rear bumper and trunk are badly damaged. \
The other driver has State Farm, policy SF-443892. My car is a 2022 \
Honda Civic. Officer gave me case number 2025-MP-00481.`;

const CUSTOMER = {
  id: "C-1234",
  policyType: "auto-premium",
  coverageLimit: 50_000,
  deductible: 500,
};

// fraud check uses claim history — in production, query a risk database
const FRAUD_HISTORY: Record<string, { claims12mo: number; fraudFlags: number }> = {
  "C-1234": { claims12mo: 1, fraudFlags: 0 }, // low risk
};

// coverage rules by policy type
const COVERAGE: Record<string, { coveredTypes: string[]; limit: number; deductible: number }> = {
  "auto-premium": { coveredTypes: ["auto"], limit: 50_000, deductible: 500 },
  "home-basic":   { coveredTypes: ["home"], limit: 25_000, deductible: 1_000 },
};


// --- Structured output schemas ---
// The LLM returns typed data at two pipeline steps:
// 1. Classification — claim type and estimated cost
// 2. Extraction — specific fields that vary by claim category

const classificationSchema = z.object({
  category: z.enum(["auto", "home"]),
  estimatedAmount: z.number().describe("Estimated claim amount in dollars"),
});

const autoExtractionSchema = z.object({
  vehicles: z.string().describe("Vehicles involved in the incident"),
  damage: z.string().describe("Description of damage"),
  policeReport: z.string().nullable().describe("Police report number if mentioned"),
});

const homeExtractionSchema = z.object({
  damageType: z.string().describe("Type of home damage (fire, water, etc.)"),
  rooms: z.string().describe("Affected rooms or areas"),
  contractorEstimate: z.number().nullable().describe("Contractor estimate if mentioned"),
});


// --- LLM-powered steps ---
// Each function makes one LLM call with structured output.
// Output.object() constrains the response to match the Zod schema.

async function classifyClaim(claimText: string) {
  const { output } = await generateText({
    model: openai(LLM_MODEL),
    output: Output.object({ schema: classificationSchema }),
    system: `\
You are an insurance claim classifier. Determine:
1. category: "auto" for vehicle claims, "home" for property claims
2. estimatedAmount: dollar estimate based on the damage described`,
    prompt: claimText,
  });
  return output!;
}

async function extractAuto(claimText: string, retryHint = "") {
  let prompt = claimText;
  if (retryHint) {
    prompt += `\n\nPrevious extraction was missing: ${retryHint}. Look carefully.`;
  }
  const { output } = await generateText({
    model: openai(LLM_MODEL),
    output: Output.object({ schema: autoExtractionSchema }),
    system: `\
Extract structured details from this auto insurance claim.
Return null for optional fields not mentioned in the text.`,
    prompt,
  });
  return output!;
}

async function extractHome(claimText: string, retryHint = "") {
  let prompt = claimText;
  if (retryHint) {
    prompt += `\n\nPrevious extraction was missing: ${retryHint}. Look carefully.`;
  }
  const { output } = await generateText({
    model: openai(LLM_MODEL),
    output: Output.object({ schema: homeExtractionSchema }),
    system: `\
Extract structured details from this home insurance claim.
Return null for optional fields not mentioned in the text.`,
    prompt,
  });
  return output!;
}


// --- Deterministic steps (plain code, not LLM) ---
// Business rules that must be exact, auditable, and reproducible.

function checkFraud(customerId: string) {
  const history = FRAUD_HISTORY[customerId] ?? { claims12mo: 0, fraudFlags: 0 };
  const score = history.claims12mo * 10 + history.fraudFlags * 30;
  return { fraudScore: score, flagged: score > 50 };
}

function validateExtraction(extraction: Record<string, unknown>, category: string) {
  const required: Record<string, string[]> = {
    auto: ["vehicles", "damage"],
    home: ["damageType", "rooms"],
  };
  return (required[category] ?? []).filter((f) => !extraction[f]);
}

function decide(category: string, amount: number, customer: typeof CUSTOMER) {
  const policy = COVERAGE[customer.policyType];
  if (!policy.coveredTypes.includes(category)) {
    return { decision: "deny", reason: "Not covered under policy" };
  }
  if (amount <= 1000) {
    return { decision: "approve", reason: "Under auto-approval threshold" };
  }
  return { decision: "review", reason: "Amount exceeds auto-approval, adjuster required" };
}


// --- Pipeline orchestration ---
// No graph abstraction — the pipeline IS the code. Branching is if/else,
// retry is a for loop, parallel could be Promise.all (kept sequential here).
// This is shorter than a graph definition, but you lose visual debugging,
// state snapshots, and the ability to test nodes independently.
// See flow.txt for the visual diagram of what this code implements.

// step 1: classify + fraud check (independent — could run in parallel with Promise.all)
const classification = await classifyClaim(CLAIM_TEXT);
const fraud = checkFraud(CUSTOMER.id);
console.log(`Classify: ${classification.category}, $${classification.estimatedAmount}`);
console.log(`Fraud:    score=${fraud.fraudScore}, flagged=${fraud.flagged}`);

// step 2: fraud gate — reject immediately if flagged
if (fraud.flagged) {
  console.log("\nREJECTED — fraud risk too high");
  process.exit();
}

// step 3: extract details based on claim category (with retry for missing fields)
// auto claims need vehicle/damage/police info; home claims need damage type/rooms/estimate
let extraction: Record<string, unknown> = {};
let retryHint = "";

for (let attempt = 0; attempt < 3; attempt++) {
  extraction =
    classification.category === "auto"
      ? await extractAuto(CLAIM_TEXT, retryHint)
      : await extractHome(CLAIM_TEXT, retryHint);

  const missing = validateExtraction(extraction, classification.category);
  if (missing.length === 0) break;

  retryHint = missing.join(", ");
  console.log(`Retry ${attempt + 1}/2: missing ${missing}`);

  if (attempt === 2) {
    console.log("\nFAILED — extraction incomplete after retries");
    process.exit();
  }
}

console.log(`Extract:  ${JSON.stringify(extraction)}`);

// step 4: decide
const result = decide(classification.category, classification.estimatedAmount, CUSTOMER);
console.log(`\nDecision: ${result.decision.toUpperCase()}`);
console.log(`Reason:   ${result.reason}`);
// Classify: auto, $5000
// Fraud:    score=10, flagged=false
// Extract:  {"vehicles":"2022 Honda Civic","damage":"rear bumper and trunk...","policeReport":"2025-MP-00481"}
// Decision: REVIEW
// Reason:   Amount exceeds auto-approval, adjuster required
