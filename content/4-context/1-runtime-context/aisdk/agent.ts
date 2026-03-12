import { ToolLoopAgent, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

// mock database — in production these are real queries
const ORDERS: Record<string, { id: string; item: string; status: string }[]> = {
  user_123: [
    { id: "ORD_99", item: "Laptop Stand", status: "shipped" },
    { id: "ORD_100", item: "USB Hub", status: "processing" },
  ],
};

// status is chosen by the LLM — userId comes from your app (auth, session, etc.)
// only status appears in the tool schema — the LLM can't see or fabricate userId
function createTools(userId: string) {
  const getOrders = tool({
    description: "Get orders filtered by status.",
    inputSchema: z.object({ status: z.string() }),
    execute: async ({ status }) => {
      console.log(`-> call: get_orders(${status}) for ${userId}`);
      const matches = ORDERS[userId].filter((o) => o.status === status);
      const result = matches.map((o) => `${o.id}: ${o.item}`).join(", ") || "No orders found.";
      console.log(`-> result: ${result}`);
      return result;
    },
  });
  return { getOrders };
}

const tools = createTools("user_123");

const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  tools,
});

const result = await agent.generate({
  prompt: "Do I have any shipped orders?",
});
console.log(result.text);
// -> call: get_orders(shipped) for user_123
// -> result: ORD_99: Laptop Stand
// "Your shipped order is ORD_99: Laptop Stand."
