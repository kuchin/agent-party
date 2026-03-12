import { Agent } from "@mastra/core/agent";
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

// model specified as "provider/model-name" string
const LLM_MODEL = "openai/gpt-5.4";

// nested Zod schemas with enums, constraints, defaults, and descriptions
const placeOrder = createTool({
  id: "place-order",
  description: "Place an order with line items and shipping details",
  inputSchema: z.object({
    items: z.array(
      z.object({
        sku: z.string().describe("Product SKU, e.g. 'SKU_921'"),
        quantity: z.number().int().min(1).describe("Number of units to order"),
        giftWrap: z.boolean().default(false).describe("Wrap item in gift packaging"),
      }),
    ),
    shipping: z.object({
      street: z.string(),
      city: z.string(),
      zip: z.string().describe("Postal/ZIP code"),
      country: z.string().describe("ISO 3166-1 alpha-2 country code, e.g. 'US'"),
    }),
    shippingMethod: z.enum(["standard", "express", "overnight"]).default("standard"),
    notes: z.string().optional().describe("Delivery instructions"),
  }),
  execute: async ({ items, shipping, shippingMethod }) => {
    console.log(`-> call: placeOrder(${items.length} items, ${shippingMethod})`);
    const summary = items
      .map((i) => `${i.quantity}× ${i.sku}${i.giftWrap ? " (gift)" : ""}`)
      .join(", ");
    const result = [
      `Order ORD_743 confirmed:`,
      `  ${summary}.`,
      `  ${shippingMethod} to ${shipping.city}.`,
    ].join("\n");
    console.log(`-> result: ${result}`);
    return result;
  },
});

const agent = new Agent({
  name: "order-agent",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  tools: { placeOrder },
});

const result = await agent.generate(
  `Order 2 of SKU_921 with gift wrap and 1 of SKU_114.
  Ship overnight to 100 Main St, San Francisco 94105, US.
  Leave at the back door.`,
);
console.log(result.text);
// -> call: placeOrder(2 items, overnight)
// -> result: Order ORD_743 confirmed:
//   2× SKU_921 (gift), 1× SKU_114.
//   overnight to San Francisco.
// "Done - order ORD_743 is confirmed.
// - 2 × SKU_921, gift wrapped
// - 1 × SKU_114
// - Shipping: overnight
// - Address: 100 Main St, San Francisco, 94105, US
// - Note: Leave at the back door."
