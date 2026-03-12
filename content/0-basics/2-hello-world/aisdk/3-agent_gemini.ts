import { generateText } from "ai";
import { google } from "@ai-sdk/google";

const LLM_MODEL = "gemini-pro-latest";

const { text } = await generateText({
  model: google(LLM_MODEL),
  prompt: "What is the capital of France?",
});
console.log(text);
// "Paris."
