import { Agent } from "@mastra/core/agent";
import { Memory } from "@mastra/memory";

const LLM_MODEL = "openai/gpt-5.4";

// observational memory: background agents compress conversation automatically
// observer watches for token growth, creates concise notes (5-40x compression)
// reflector further condenses when observations accumulate
// no compaction pause — runs transparently alongside normal conversation
const agent = new Agent({
  name: "assistant",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  memory: new Memory({
    options: {
      lastMessages: 20,
      observationalMemory: true,
    },
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
