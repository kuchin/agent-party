import { Agent } from "@mastra/core/agent";
import { Memory } from "@mastra/memory";

const LLM_MODEL = "openai/gpt-5.4";

// Memory manages conversation state — same thread restores history
const agent = new Agent({
  name: "assistant",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  memory: new Memory(),
});

const memoryConfig = { memory: { thread: "chat_1", resource: "user_1" } };

// turn 1
const result1 = await agent.generate(
  "What is the capital of France?",
  memoryConfig,
);
console.log(result1.text);
// "The capital of France is Paris."

// turn 2 — same thread, memory restores history automatically
const result2 = await agent.generate(
  "What is its population?",
  memoryConfig,
);
console.log(result2.text);
// "The population of Paris is approximately 2.1 million..."
