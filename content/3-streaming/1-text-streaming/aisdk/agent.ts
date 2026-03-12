import { streamText } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

// streamText returns an object with async iterable stream properties
const result = streamText({
  model: openai(LLM_MODEL),
  prompt: "Explain what an API is in a few sentences.",
});
for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
console.log();
// An API (Application Programming Interface) is a set of rules and protocols
// that allows different software applications to communicate with each other...
