import { Agent } from "@mastra/core/agent";
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

// model specified as "provider/model-name" string
const LLM_MODEL = "openai/gpt-5.4";

const CUSTOMERS: Record<string, string> = { "alice@example.com": "CUS_8f3a2b" };
const BALANCES: Record<string, string> = { CUS_8f3a2b: "$1,432.50" };

const lookupCustomer = createTool({
  id: "lookup-customer",
  description: "Look up a customer by email and return their internal ID",
  inputSchema: z.object({ email: z.string() }),
  execute: async ({ email }) => {
    console.log(`-> call: lookupCustomer(${email})`);
    const result = CUSTOMERS[email];
    console.log(`-> result: ${result}`);
    return result;
  },
});

const getBalance = createTool({
  id: "get-balance",
  description: "Get the account balance for a customer ID",
  inputSchema: z.object({ customerId: z.string() }),
  execute: async ({ customerId }) => {
    console.log(`-> call: getBalance(${customerId})`);
    const result = BALANCES[customerId];
    console.log(`-> result: ${result}`);
    return result;
  },
});

const agent = new Agent({
  name: "multi-step-agent",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  tools: { lookupCustomer, getBalance },
});

// This is the basic ReAct loop:
// the model calls one tool, sees the result, then decides the next step.
// maxSteps controls how many times Mastra can loop (default: 1).
const result = await agent.generate(
  "What's the balance for alice@example.com?",
  { maxSteps: 3 },
);
console.log(result.text);
// -> call: lookupCustomer(alice@example.com)
// -> result: CUS_8f3a2b
// -> call: getBalance(CUS_8f3a2b)
// -> result: $1,432.50
// "The balance for alice@example.com is $1,432.50."
