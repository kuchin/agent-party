import { generateText, type ModelMessage } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

// sliding window: keep last N messages, discard everything older
// cheapest — zero latency, but complete context loss beyond the window
const WINDOW = 10;
const messages: ModelMessage[] = [];

async function chat(message: string): Promise<string> {
  messages.push({ role: "user", content: message });
  const window = messages.slice(-WINDOW);
  const result = await generateText({
    model: openai(LLM_MODEL),
    messages: window,
  });
  messages.push({ role: "assistant", content: result.text });
  return result.text;
}

console.log(await chat("What is the capital of France?"));
console.log(await chat("What is its population?"));
