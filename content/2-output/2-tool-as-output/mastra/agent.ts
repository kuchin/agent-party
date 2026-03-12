import { Agent } from "@mastra/core/agent";
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

// model specified as "provider/model-name" string
const LLM_MODEL = "openai/gpt-5.4";

const ARTICLE = `\
BrightHome Inc. of Austin, Texas, has recalled 142,000 SmartHeat Pro
space heaters due to fire and burn hazards. The company received 23
reports of overheating, including 4 fires and 2 minor burn injuries.
No deaths have been reported. The heaters were sold at HomeBase,
WarmthPlus, and Amazon.com from September 2023 through February 2024
for between $89 and $149.`;

// instead of structuredOutput, use a tool call to extract data —
// the LLM "calls" the function, and we capture the arguments
const extractRecall = createTool({
  id: "extract-recall",
  description: "Extract product recall information from an article.",
  inputSchema: z.object({
    product: z.string(),
    company: z.string(),
    units_affected: z.number().int(),
    hazard: z.string().describe("Primary hazard"),
    injuries_reported: z.number().int(),
    fatalities: z.boolean(),
    retailers: z.array(z.string()).describe("Stores that sold the product"),
  }),
  execute: async (args) => {
    console.log(args);
    return "Extracted.";
  },
});

const agent = new Agent({
  name: "extractor",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  tools: { extractRecall },
});

const result = await agent.generate(
  "Extract recall data from this article:\n\n" + ARTICLE,
);
// { product: 'SmartHeat Pro', company: 'BrightHome Inc.', units_affected: 142000,
//   hazard: 'fire and burn', injuries_reported: 2, fatalities: false,
//   retailers: ['HomeBase', 'WarmthPlus', 'Amazon.com'] }
