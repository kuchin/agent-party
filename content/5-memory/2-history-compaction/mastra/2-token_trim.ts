import { Agent } from "@mastra/core/agent";
import { Memory } from "@mastra/memory";

const LLM_MODEL = "openai/gpt-5.4";

// token-aware: generous window + semantic recall for important older context
// lastMessages limits what's sent to the model each turn
// semanticRecall retrieves relevant older messages beyond the window,
// so important context isn't lost after trimming
const agent = new Agent({
  name: "assistant",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  memory: new Memory({
    options: {
      lastMessages: 40,
      semanticRecall: { topK: 3, messageRange: 2 },
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
