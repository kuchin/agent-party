import { createWorkflow, createStep } from "@mastra/core/workflows";
import { Agent } from "@mastra/core/agent";
import { z } from "zod";

const LLM_MODEL = "openai/gpt-5.4";

// --- Mock data ---
// In production these come from the customer portal, policy database, and risk engine.

const CLAIM_TEXT = `\
I was in a car accident on Highway 101 on March 3rd. Another vehicle \
rear-ended me at a stoplight. My rear bumper and trunk are badly damaged. \
The other driver has State Farm, policy SF-443892. My car is a 2022 \
Honda Civic. Officer gave me case number 2025-MP-00481.`;

const CUSTOMER = { id: "C-1234", policyType: "auto-premium" };

const FRAUD_HISTORY: Record<string, { claims12mo: number; fraudFlags: number }> = {
  "C-1234": { claims12mo: 1, fraudFlags: 0 },
};

const COVERAGE: Record<string, { coveredTypes: string[]; limit: number; deductible: number }> = {
  "auto-premium": { coveredTypes: ["auto"], limit: 50_000, deductible: 500 },
  "home-basic":   { coveredTypes: ["home"], limit: 25_000, deductible: 1_000 },
};


// --- Schemas ---
// Typed contracts between steps. Mastra validates these at each step boundary.

const claimInputSchema = z.object({
  claimText: z.string(),
  customerId: z.string(),
});

const classifySchema = z.object({
  category: z.enum(["auto", "home"]),
  estimatedAmount: z.number().describe("Estimated claim amount in dollars"),
});

const fraudSchema = z.object({
  fraudScore: z.number(),
  flagged: z.boolean(),
});

const autoExtractionSchema = z.object({
  vehicles: z.string().describe("Vehicles involved in the incident"),
  damage: z.string().describe("Description of damage"),
  policeReport: z.string().nullable().describe("Police report number if mentioned"),
});

const homeExtractionSchema = z.object({
  damageType: z.string().describe("Type of home damage"),
  rooms: z.string().describe("Affected rooms or areas"),
  contractorEstimate: z.number().nullable().describe("Contractor estimate if mentioned"),
});

const decisionSchema = z.object({
  decision: z.string(),
  reason: z.string(),
});


// --- Agent for LLM-powered steps ---

const claimAgent = new Agent({
  name: "claim-processor",
  model: LLM_MODEL,
  instructions: "You process insurance claims. Follow the specific task instructions.",
});


// --- Pipeline steps ---
// Each step has typed input/output schemas. Mastra validates data at each boundary.

// step 1a: classify the claim (LLM) — runs in parallel with fraud check
const classifyStep = createStep({
  id: "classify",
  inputSchema: claimInputSchema,
  outputSchema: classifySchema,
  execute: async ({ inputData }) => {
    const result = await claimAgent.generate(
      `Classify this insurance claim. Determine the category (auto or home) and estimate the amount:\n${inputData.claimText}`,
      { structuredOutput: { schema: classifySchema } },
    );
    console.log(`Classify: ${result.object!.category}, $${result.object!.estimatedAmount}`);
    return result.object!;
  },
});

// step 1b: check fraud (deterministic) — runs in parallel with classify
const fraudCheckStep = createStep({
  id: "fraud-check",
  inputSchema: claimInputSchema,
  outputSchema: fraudSchema,
  execute: async ({ inputData }) => {
    const history = FRAUD_HISTORY[inputData.customerId] ?? { claims12mo: 0, fraudFlags: 0 };
    const score = history.claims12mo * 10 + history.fraudFlags * 30;
    const flagged = score > 50;
    console.log(`Fraud:    score=${score}, flagged=${flagged}`);
    return { fraudScore: score, flagged };
  },
});

// step 2: fraud gate — bail() exits the entire workflow if fraud is flagged
const fraudGateStep = createStep({
  id: "fraud-gate",
  // after .parallel(), output is keyed by step id
  inputSchema: z.object({ classify: classifySchema, "fraud-check": fraudSchema }),
  outputSchema: z.object({ category: z.enum(["auto", "home"]), estimatedAmount: z.number() }),
  execute: async ({ inputData, bail }) => {
    if (inputData["fraud-check"].flagged) {
      console.log("\nREJECTED — fraud risk too high");
      return bail({ decision: "reject", reason: "Fraud risk too high" });
    }
    return {
      category: inputData.classify.category,
      estimatedAmount: inputData.classify.estimatedAmount,
    };
  },
});

// step 3+4: extract details and validate (with retry loop inside the step)
// handles category branching internally — auto vs home need different schemas
const extractStep = createStep({
  id: "extract",
  inputSchema: z.object({ category: z.enum(["auto", "home"]), estimatedAmount: z.number() }),
  outputSchema: z.object({
    category: z.enum(["auto", "home"]),
    estimatedAmount: z.number(),
    extraction: z.record(z.unknown()),
  }),
  execute: async ({ inputData, getInitData }) => {
    const initData = await getInitData();
    const schema = inputData.category === "auto" ? autoExtractionSchema : homeExtractionSchema;
    const required = inputData.category === "auto" ? ["vehicles", "damage"] : ["damageType", "rooms"];

    // extract with retry for missing fields (1 initial + up to 2 retries)
    let extraction: Record<string, unknown> = {};
    let retryHint = "";
    for (let attempt = 0; attempt < 3; attempt++) {
      let prompt = `Extract details from this ${inputData.category} insurance claim:\n${initData.claimText}`;
      if (retryHint) prompt += `\n\nPrevious extraction was missing: ${retryHint}. Look carefully.`;
      const result = await claimAgent.generate(prompt, { structuredOutput: { schema } });
      extraction = result.object as Record<string, unknown>;
      const missing = required.filter((f) => !extraction[f]);
      if (!missing.length) break;
      retryHint = missing.join(", ");
      console.log(`Retry ${attempt + 1}/2: missing [${retryHint}]`);
    }
    console.log(`Extract:  ${JSON.stringify(extraction)}`);
    return { category: inputData.category, estimatedAmount: inputData.estimatedAmount, extraction };
  },
});

// step 5: apply coverage rules (deterministic)
const decideStep = createStep({
  id: "decide",
  inputSchema: z.object({
    category: z.enum(["auto", "home"]),
    estimatedAmount: z.number(),
    extraction: z.record(z.unknown()),
  }),
  outputSchema: decisionSchema,
  execute: async ({ inputData }) => {
    const policy = COVERAGE[CUSTOMER.policyType];
    let result: { decision: string; reason: string };
    if (!policy.coveredTypes.includes(inputData.category)) {
      result = { decision: "deny", reason: "Not covered under policy" };
    } else if (inputData.estimatedAmount <= 1000) {
      result = { decision: "approve", reason: "Under auto-approval threshold" };
    } else {
      result = { decision: "review", reason: "Amount exceeds auto-approval, adjuster required" };
    }
    console.log(`\nDecision: ${result.decision.toUpperCase()}`);
    console.log(`Reason:   ${result.reason}`);
    return result;
  },
});


// --- Workflow definition ---
// The workflow IS the orchestration. Steps are typed, chained, and validated.
// .parallel() runs classify + fraud check simultaneously.
// bail() in the fraud gate exits the entire workflow early.
// Compare with the raw SDK version where this is all if/else in a script.
// See flow.txt for the visual diagram this workflow implements.

const workflow = createWorkflow({
  id: "claim-pipeline",
  inputSchema: claimInputSchema,
  outputSchema: decisionSchema,
})
  .parallel([classifyStep, fraudCheckStep])
  .then(fraudGateStep)
  .then(extractStep)
  .then(decideStep)
  .commit();

const run = await workflow.createRun();
const result = await run.start({
  inputData: { claimText: CLAIM_TEXT, customerId: CUSTOMER.id },
});
console.log(result.result);
// Classify: auto, $5000
// Fraud:    score=10, flagged=false
// Extract:  {"vehicles":"2022 Honda Civic","damage":"rear bumper and trunk...","policeReport":"2025-MP-00481"}
// Decision: REVIEW
// Reason:   Amount exceeds auto-approval, adjuster required
