import { ToolLoopAgent, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";
const FAST_MODEL = "gpt-5-mini";

// --- Mock data ---

// past support tickets — in production this would be a database or search index
const TICKETS: string[] = [
  "TK-301: Double charge on Pro plan — Refunded (2025-02-15)",
  "TK-287: Charged twice for March — Refunded (2025-03-01)",
  "TK-305: Cannot access API — Fixed API key (2025-03-03)",
];

// customer invoices — in production this would query Stripe, billing DB, etc.
const INVOICES: string[] = [
  "INV-440: $49 on 2025-03-01 (paid)",
  "INV-441: $49 on 2025-03-01 (paid — duplicate)",
];

// --- Child tools (used by specialists, not by the parent) ---

const searchTickets = tool({
  description: "Search past support tickets by keyword",
  inputSchema: z.object({ query: z.string() }),
  execute: async ({ query }) => {
    console.log(`-> call: searchTickets(${JSON.stringify(query)})`);
    // split into words so partial matches work — the LLM might send
    // "customers charged twice" but individual words like "charge" still match
    const words = query.toLowerCase().split(/\s+/);
    const matches = TICKETS.filter((t) => {
      const lower = t.toLowerCase();
      return words.some((w) => lower.includes(w));
    });
    const result = matches.length > 0 ? matches.join("\n") : "No similar tickets found.";
    console.log(`-> result: ${matches.length} tickets found`);
    return result;
  },
});

const lookupInvoices = tool({
  description: "Look up the current customer's recent invoices",
  inputSchema: z.object({}),
  execute: async () => {
    console.log("-> call: lookupInvoices()");
    const result = INVOICES.join("\n");
    console.log(`-> result: ${INVOICES.length} invoices`);
    return result;
  },
});

// --- Specialist: ticket search ---
// Specializes in RETRIEVAL — finding patterns in past support data.
// Uses a faster/cheaper model because the task is lookup, not reasoning.

const ticketAgent = new ToolLoopAgent({
  model: openai(FAST_MODEL),
  system: `\
You search past support tickets and summarize what you find.
Report how many similar issues exist and how they were resolved.
`,
  tools: { searchTickets },
});

// --- Specialist: billing ---
// Specializes in POLICY — applying business rules to specific situations.
// Uses the main model because refund decisions require judgment.

const billingAgent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  system: `\
You are a billing specialist. Look up invoices and apply refund policy.
Refund policy: duplicate charges are always refundable.
`,
  tools: { lookupInvoices },
});

// --- Parent tools (each wraps a subagent) ---
// The parent has no domain tools — it only delegates to specialists.
// This keeps each specialist's context focused: the ticket searcher never sees
// invoice data, and the billing agent never sees ticket history.
// Without this separation, irrelevant context from one domain can confuse
// reasoning in another (sometimes called "context poisoning").
// See flow.txt for the delegation diagram this code implements.

const searchPreviousTickets = tool({
  description: "Search past tickets for similar issues",
  inputSchema: z.object({ query: z.string() }),
  execute: async ({ query }) => {
    console.log(`-> call: searchPreviousTickets(${JSON.stringify(query)})`);
    // call the subagent — the parent sees only the final answer
    const result = await ticketAgent.generate({ prompt: query });
    return result.text;
  },
});

const checkBilling = tool({
  description: "Ask the billing specialist about charges, invoices, or refunds",
  inputSchema: z.object({ question: z.string() }),
  execute: async ({ question }) => {
    console.log(`-> call: checkBilling(${JSON.stringify(question)})`);
    const result = await billingAgent.generate({ prompt: question });
    return result.text;
  },
});

// --- Parent agent ---
// ToolLoopAgent handles the multi-step loop automatically.
// The parent delegates to specialist agents through the wrapper tools above.

const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  system: `\
You are a customer support agent. Use your specialists:
searchPreviousTickets checks for similar past issues,
checkBilling handles billing or refund questions.
Combine their findings into a single helpful response.
`,
  tools: { searchPreviousTickets, checkBilling },
});

const result = await agent.generate({
  prompt: `\
I was charged twice this month.
Has this happened to other customers? Can I get a refund?
`,
});
console.log(result.text);
// -> call: searchPreviousTickets("double charge")
//   -> call: searchTickets("double charge")
//   -> result: 2 tickets found
// -> call: checkBilling("charged twice, eligible for refund?")
//   -> call: lookupInvoices()
//   -> result: 2 invoices
// "We've seen similar double-charge reports — both resolved with refunds.
//  You have two $49 charges from March 1st. Duplicate charges are always
//  refundable — I'll process your refund right away."
