import { Agent } from "@mastra/core/agent";
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

// model specified as "provider/model-name" string
const LLM_MODEL = "openai/gpt-5.4";

// inputSchema defines typed parameters the LLM must provide
const getWeather = createTool({
  id: "get-weather",
  description: "Get the current weather for a city",
  inputSchema: z.object({ city: z.string() }),
  execute: async ({ city }) => {
    console.log(`-> call: getWeather(${city})`);
    const result = `The weather in ${city} is 72°F and sunny.`;
    console.log(`-> result: ${result}`);
    return result;
  },
});

const agent = new Agent({
  name: "weather-agent",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  tools: { getWeather },
});

const result = await agent.generate("What's the weather in Paris?");
console.log(result.text);
// -> call: getWeather(Paris)
// -> result: The weather in Paris is 72°F and sunny.
// "It's 72°F and sunny in Paris."
