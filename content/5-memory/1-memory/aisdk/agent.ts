import { generateText, type ModelMessage } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

// AI SDK has no built-in memory — store messages yourself
const store: Record<string, ModelMessage[]> = {};

async function chat(threadId: string, message: string): Promise<string> {
  const history = store[threadId] ?? [];
  history.push({ role: "user", content: message });
  const result = await generateText({ model: openai(LLM_MODEL), messages: history });
  history.push({ role: "assistant", content: result.text });
  store[threadId] = history;
  return result.text;
}

// turn 1
console.log(await chat("chat_1", "What is the capital of France?"));
// "The capital of France is Paris."

// turn 2 — same thread, history is restored from the store
console.log(await chat("chat_1", "What is its population?"));
// "The population of Paris is approximately 2.1 million..."
