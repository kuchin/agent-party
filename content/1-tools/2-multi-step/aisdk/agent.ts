import { ToolLoopAgent, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

const CUSTOMERS: Record<string, string> = { "alice@example.com": "CUS_8f3a2b" };
const BALANCES: Record<string, string> = { CUS_8f3a2b: "$1,432.50" };

const lookupCustomer = tool({
  description: "Look up a customer by email and return their internal ID",
  inputSchema: z.object({ email: z.string() }),
  execute: async ({ email }) => {
    console.log(`-> call: lookupCustomer(${email})`);
    const result = CUSTOMERS[email];
    console.log(`-> result: ${result}`);
    return result;
  },
});

const getBalance = tool({
  description: "Get the account balance for a customer ID",
  inputSchema: z.object({ customerId: z.string() }),
  execute: async ({ customerId }) => {
    console.log(`-> call: getBalance(${customerId})`);
    const result = BALANCES[customerId];
    console.log(`-> result: ${result}`);
    return result;
  },
});

// ToolLoopAgent handles multi-step automatically (defaults to 20 steps max)
const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  tools: { lookupCustomer, getBalance },
});

const result = await agent.generate({
  prompt: "What's the balance for alice@example.com?",
});
console.log(result.text);
// -> call: lookupCustomer(alice@example.com)
// -> result: CUS_8f3a2b
// -> call: getBalance(CUS_8f3a2b)
// -> result: $1,432.50
// "The balance for alice@example.com is $1,432.50."
