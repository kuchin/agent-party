import { generateText, Output } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

const ticketAnalysis = z.object({
  category: z.enum(["billing", "technical", "account", "product"]),
  priority: z.enum(["low", "medium", "high", "critical"]),
  sentiment: z.enum(["positive", "neutral", "negative"]),
  requires_escalation: z.boolean(),
  summary: z.string().describe("One-sentence summary of the issue"),
  suggested_tags: z.array(z.string()).describe("1-4 short labels for routing"),
});

// Output.object() constrains the response to match the Zod schema
const { output } = await generateText({
  model: openai(LLM_MODEL),
  output: Output.object({ schema: ticketAnalysis }),
  prompt: `Analyze this support ticket:
  'I've been charged twice for my Pro subscription this month.
  I contacted support 3 days ago and haven't heard back.
  If this isn't resolved by Friday I'm switching to a competitor.'`,
});
console.log(output);
// { category: 'billing', priority: 'high', sentiment: 'negative',
//   requires_escalation: true, summary: 'Customer was double-charged...',
//   suggested_tags: ['billing', 'double-charge', 'escalation', 'churn-risk'] }
