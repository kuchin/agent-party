import { Agent } from "@mastra/core/agent";
import { Memory } from "@mastra/memory";

const LLM_MODEL = "openai/gpt-5.4";

// sliding window: keep last N messages, discard everything older
// built into Memory — one config option, no custom code needed
const agent = new Agent({
  name: "assistant",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  memory: new Memory({
    options: { lastMessages: 10 },
  }),
});

const memoryConfig = { memory: { thread: "chat_1", resource: "user_1" } };

const result1 = await agent.generate(
  "What is the capital of France?",
  memoryConfig,
);
console.log(result1.text);

const result2 = await agent.generate(
  "What is its population?",
  memoryConfig,
);
console.log(result2.text);
