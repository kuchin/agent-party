import { Agent } from "@mastra/core/agent";

// model specified as "provider/model-name" string
const LLM_MODEL = "anthropic/claude-opus-4-6";

const agent = new Agent({
  name: "hello-world",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
});

const result = await agent.generate("What is the capital of France?");
console.log(result.text);
// "Paris."
