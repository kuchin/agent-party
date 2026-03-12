import { Agent } from "@mastra/core/agent";
import { z } from "zod";

// model specified as "provider/model-name" string
const LLM_MODEL = "openai/gpt-5.4";

const ticketAnalysis = z.object({
  category: z.enum(["billing", "technical", "account", "product"]),
  priority: z.enum(["low", "medium", "high", "critical"]),
  sentiment: z.enum(["positive", "neutral", "negative"]),
  requires_escalation: z.boolean(),
  summary: z.string().describe("One-sentence summary of the issue"),
  suggested_tags: z.array(z.string()).describe("1-4 short labels for routing"),
});

const agent = new Agent({
  name: "ticket-analyzer",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
});

// structuredOutput constrains the response to match the Zod schema
const result = await agent.generate(
  `Analyze this support ticket:
  'I've been charged twice for my Pro subscription this month.
  I contacted support 3 days ago and haven't heard back.
  If this isn't resolved by Friday I'm switching to a competitor.'`,
  { structuredOutput: { schema: ticketAnalysis } },
);
console.log(result.object);
// { category: 'billing', priority: 'high', sentiment: 'negative',
//   requires_escalation: true, summary: 'Customer was double-charged...',
//   suggested_tags: ['billing', 'double-charge', 'escalation', 'churn-risk'] }
