import { ToolLoopAgent, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

// tool() creates a typed tool with Zod inputSchema
const getWeather = tool({
  description: "Get the current weather for a city",
  inputSchema: z.object({ city: z.string() }),
  execute: async ({ city }) => {
    console.log(`-> call: getWeather(${city})`);
    const result = `The weather in ${city} is 72°F and sunny.`;
    console.log(`-> result: ${result}`);
    return result;
  },
});

// ToolLoopAgent loops automatically — no step count needed for single tool
const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  tools: { getWeather },
});

const result = await agent.generate({
  prompt: "What's the weather in Paris?",
});
console.log(result.text);
// -> call: getWeather(Paris)
// -> result: The weather in Paris is 72°F and sunny.
// "It's 72°F and sunny in Paris."
