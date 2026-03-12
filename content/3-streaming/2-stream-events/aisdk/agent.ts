import { ToolLoopAgent, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

const CUSTOMERS: Record<string, string> = { "alice@example.com": "CUS_8f3a2b" };
const BALANCES: Record<string, string> = { CUS_8f3a2b: "$1,432.50" };

const lookupCustomer = tool({
  description: "Look up a customer by email and return their internal ID",
  inputSchema: z.object({ email: z.string() }),
  execute: async ({ email }) => CUSTOMERS[email],
});

const getBalance = tool({
  description: "Get the account balance for a customer ID",
  inputSchema: z.object({ customerId: z.string() }),
  execute: async ({ customerId }) => BALANCES[customerId],
});

const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  tools: { lookupCustomer, getBalance },
});

// agent.stream() is async — fullStream yields typed events
const result = await agent.stream({
  prompt: "What's the balance for alice@example.com?",
});
for await (const chunk of result.fullStream) {
  if (chunk.type === "tool-call") {
    console.log(`-> call: ${chunk.toolName}(${JSON.stringify(chunk.input)})`);
  } else if (chunk.type === "tool-result") {
    console.log(`-> result: ${chunk.output}`);
  } else if (chunk.type === "text-delta") {
    process.stdout.write(chunk.text);
  }
}
console.log();
// -> call: lookupCustomer({"email":"alice@example.com"})
// -> result: CUS_8f3a2b
// -> call: getBalance({"customerId":"CUS_8f3a2b"})
// -> result: $1,432.50
// The balance for alice@example.com is $1,432.50.
