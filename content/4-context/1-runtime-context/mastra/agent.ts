import { Agent } from "@mastra/core/agent";
import { createTool } from "@mastra/core/tools";
import { RequestContext } from "@mastra/core/request-context";
import { z } from "zod";

const LLM_MODEL = "openai/gpt-5.4";

// mock database — in production these are real queries
const ORDERS: Record<string, { id: string; item: string; status: string }[]> = {
  user_123: [
    { id: "ORD_99", item: "Laptop Stand", status: "shipped" },
    { id: "ORD_100", item: "USB Hub", status: "processing" },
  ],
};

// status is chosen by the LLM — userId comes from your app (auth, session, etc.)
// requestContext is hidden from the LLM — it can't see or fabricate userId
const getOrders = createTool({
  id: "get-orders",
  description: "Get orders filtered by status.",
  inputSchema: z.object({ status: z.string() }),
  requestContextSchema: z.object({ userId: z.string() }),
  execute: async ({ status }, { requestContext }) => {
    const userId = requestContext.get("userId");
    console.log(`-> call: get_orders(${status}) for ${userId}`);
    const matches = ORDERS[userId].filter((o) => o.status === status);
    const result = matches.map((o) => `${o.id}: ${o.item}`).join(", ") || "No orders found.";
    console.log(`-> result: ${result}`);
    return result;
  },
});

const agent = new Agent({
  name: "order-agent",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  tools: { getOrders },
});

const requestContext = new RequestContext([["userId", "user_123"]]);

const result = await agent.generate("Do I have any shipped orders?", {
  requestContext,
});
console.log(result.text);
// -> call: get_orders(shipped) for user_123
// -> result: ORD_99: Laptop Stand
// "Your shipped order is ORD_99: Laptop Stand."
