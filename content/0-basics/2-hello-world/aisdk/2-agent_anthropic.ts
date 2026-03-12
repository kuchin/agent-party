import { generateText } from "ai";
import { anthropic } from "@ai-sdk/anthropic";

const LLM_MODEL = "claude-opus-4-6";

const { text } = await generateText({
  model: anthropic(LLM_MODEL),
  prompt: "What is the capital of France?",
});
console.log(text);
// "Paris."
