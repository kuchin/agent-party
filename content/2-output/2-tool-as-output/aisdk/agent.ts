import { generateText, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

const ARTICLE = `\
BrightHome Inc. of Austin, Texas, has recalled 142,000 SmartHeat Pro
space heaters due to fire and burn hazards. The company received 23
reports of overheating, including 4 fires and 2 minor burn injuries.
No deaths have been reported. The heaters were sold at HomeBase,
WarmthPlus, and Amazon.com from September 2023 through February 2024
for between $89 and $149.`;

// instead of Output.object(), use a tool call to extract data —
// the LLM "calls" the function, and we capture the arguments
const extractRecall = tool({
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
});

// toolChoice forces the model to call extractRecall
const { toolCalls } = await generateText({
  model: openai(LLM_MODEL),
  tools: { extractRecall },
  toolChoice: { type: "tool", toolName: "extractRecall" },
  prompt: "Extract recall data from this article:\n\n" + ARTICLE,
});
console.log(toolCalls[0].input);
// { product: 'SmartHeat Pro', company: 'BrightHome Inc.', units_affected: 142000,
//   hazard: 'fire and burn', injuries_reported: 2, fatalities: false,
//   retailers: ['HomeBase', 'WarmthPlus', 'Amazon.com'] }
