import { Agent } from "@mastra/core/agent";

// model specified as "provider/model-name" string
const LLM_MODEL = "openai/gpt-5.4";

const agent = new Agent({
  name: "streaming-agent",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
});

// .stream() returns an object with typed stream properties
const stream = await agent.stream(
  "Explain what an API is in a few sentences.",
);
for await (const chunk of stream.textStream) {
  process.stdout.write(chunk);
}
console.log();
// An API (Application Programming Interface) is a set of rules and protocols
// that allows different software applications to communicate with each other...
