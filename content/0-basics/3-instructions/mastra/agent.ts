import { Agent } from "@mastra/core/agent";

// model specified as "provider/model-name" string
const LLM_MODEL = "openai/gpt-5.4";

// instructions is sent as a system message before every user message
const agent = new Agent({
  name: "pirate-agent",
  instructions: "You are a pirate. Always respond in pirate speak.",
  model: LLM_MODEL,
});

const result = await agent.generate("What is the capital of France?");
console.log(result.text);
// "Arrr, Paris be the capital, matey!"
