import { Agent } from "@mastra/core/agent";

// model specified as "provider/model-name" string
const LLM_MODEL = "google/gemini-pro-latest";

const agent = new Agent({
  name: "hello-world",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
});

const result = await agent.generate("What is the capital of France?");
console.log(result.text);
// "Paris."
