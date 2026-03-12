import { Agent } from "@mastra/core/agent";
import { RequestContext } from "@mastra/core/request-context";

const LLM_MODEL = "openai/gpt-5.4";

// mock database — in production these are real queries
const CUSTOMERS: Record<string, { name: string; plan: string }> = {
  user_123: { name: "Acme Corp", plan: "enterprise" },
  user_456: { name: "Jane Smith", plan: "free" },
};
const OVERDUE_INVOICES: Record<string, { id: string; amount: number }[]> = {
  user_123: [{ id: "INV-42", amount: 1200 }],
  user_456: [],
};

// instructions function receives requestContext — not a static string
// the LLM sees personalized context without querying the database itself
const agent = new Agent({
  name: "support-agent",
  model: LLM_MODEL,
  instructions: ({ requestContext }) => {
    const userId = requestContext.get("userId");
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
  },
});

// same agent, same question — behavior changes based on who's asking
let requestContext = new RequestContext([["userId", "user_123"]]);
let result = await agent.generate("I need help with my account.", {
  requestContext,
});
console.log(result.text);
// "I see there's an overdue invoice on your account. Let me help
//  resolve that. As a premium customer, I can escalate directly."

requestContext = new RequestContext([["userId", "user_456"]]);
result = await agent.generate("I need help with my account.", {
  requestContext,
});
console.log(result.text);
// "Sure, I'd be happy to help! What do you need assistance with?"
