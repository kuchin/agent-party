import { Agent } from "@mastra/core/agent";

const LLM_MODEL = "openai/gpt-5.4";

const agent = new Agent({
  name: "assistant",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
});

// turn 1
const messages: { role: "user" | "assistant"; content: string }[] = [
  { role: "user", content: "What is the capital of France?" },
];
const result1 = await agent.generate(messages);
console.log(result1.text);
// "The capital of France is Paris."

// without history, the model can't resolve "its"
const noContext = await agent.generate("What is its population?");
console.log(noContext.text);
// "Could you clarify what 'its' refers to?"

// the API is stateless — pass the full conversation each call
messages.push({ role: "assistant", content: result1.text });
messages.push({ role: "user", content: "What is its population?" });

const result2 = await agent.generate(messages);
console.log(result2.text);
// "The population of Paris is approximately 2.1 million..."
