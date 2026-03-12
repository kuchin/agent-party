import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

const { text } = await generateText({
  model: openai(LLM_MODEL),
  prompt: "What is the capital of France?",
});
console.log(text);
// "Paris."
