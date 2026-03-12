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
  execute: async ({ email }) => CUSTOMERS[email],
});

const getBalance = createTool({
  id: "get-balance",
  description: "Get the account balance for a customer ID",
  inputSchema: z.object({ customerId: z.string() }),
  execute: async ({ customerId }) => BALANCES[customerId],
});

const agent = new Agent({
  name: "stream-events-agent",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  tools: { lookupCustomer, getBalance },
});

// fullStream yields typed events for the entire agent lifecycle
const stream = await agent.stream(
  "What's the balance for alice@example.com?",
  { maxSteps: 3 },
);
for await (const chunk of stream.fullStream) {
  if (chunk.type === "tool-call") {
    console.log(`-> call: ${chunk.payload.toolName}(${JSON.stringify(chunk.payload.args)})`);
  } else if (chunk.type === "tool-result") {
    console.log(`-> result: ${chunk.payload.result}`);
  } else if (chunk.type === "text-delta") {
    process.stdout.write(chunk.payload.text);
  }
}
console.log();
// -> call: lookupCustomer({"email":"alice@example.com"})
// -> result: CUS_8f3a2b
// -> call: getBalance({"customerId":"CUS_8f3a2b"})
// -> result: $1,432.50
// The balance for alice@example.com is $1,432.50.
