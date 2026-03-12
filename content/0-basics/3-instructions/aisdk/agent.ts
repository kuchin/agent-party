import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

// system is sent as a system message before the user prompt
const { text } = await generateText({
  model: openai(LLM_MODEL),
  system: "You are a pirate. Always respond in pirate speak.",
  prompt: "What is the capital of France?",
});
console.log(text);
// "Arrr, Paris be the capital, matey!"
