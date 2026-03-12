import { ToolLoopAgent } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

// mock database — in production these are real queries
const CUSTOMERS: Record<string, { name: string; plan: string }> = {
  user_123: { name: "Acme Corp", plan: "enterprise" },
  user_456: { name: "Jane Smith", plan: "free" },
};
const OVERDUE_INVOICES: Record<string, { id: string; amount: number }[]> = {
  user_123: [{ id: "INV-42", amount: 1200 }],
  user_456: [],
};

function buildInstructions(userId: string): string {
  const customer = CUSTOMERS[userId];
  const overdue = OVERDUE_INVOICES[userId];
  const lines = [`Customer: ${customer.name}, plan: ${customer.plan}.`];
  if (overdue.length) {
    lines.push(
      `ALERT: ${overdue.length} overdue invoice(s). Prioritize payment resolution.`,
    );
  }
  if (customer.plan === "enterprise") {
    lines.push("This is a premium customer. Offer direct escalation.");
  }
  return lines.join("\n");
}

// callOptionsSchema defines per-request parameters — prepareCall builds the prompt
// the LLM sees personalized context without querying the database itself
const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  callOptionsSchema: z.object({
    userId: z.string(),
  }),
  prepareCall: async ({ options, ...settings }) => ({
    ...settings,
    instructions: buildInstructions(options.userId),
  }),
});

// same agent, same question — behavior changes based on who's asking
let result = await agent.generate({
  prompt: "I need help with my account.",
  options: { userId: "user_123" },
});
console.log(result.text);
// "I see there's an overdue invoice on your account. Let me help
//  resolve that. As a premium customer, I can escalate directly."

result = await agent.generate({
  prompt: "I need help with my account.",
  options: { userId: "user_456" },
});
console.log(result.text);
// "Sure, I'd be happy to help! What do you need assistance with?"
