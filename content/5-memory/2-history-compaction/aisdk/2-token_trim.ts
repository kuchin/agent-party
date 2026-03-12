import { generateText, type ModelMessage } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

// token-aware: only trim when approaching context limit
// estimate tokens from content length — AI SDK has no built-in token counter
const TOKEN_LIMIT = 100_000;
const CHARS_PER_TOKEN = 4; // rough estimate
const messages: ModelMessage[] = [];

function estimateTokens(msgs: ModelMessage[]): number {
  return msgs.reduce(
    (sum, m) => sum + String(m.content).length / CHARS_PER_TOKEN,
    0,
  );
}

async function chat(message: string): Promise<string> {
  messages.push({ role: "user", content: message });
  // short conversations stay intact, long ones get pruned
  let window: ModelMessage[] = messages;
  if (estimateTokens(messages) > TOKEN_LIMIT) {
    window = messages.slice(-10); // approaching limit — keep recent only
  }
  const result = await generateText({
    model: openai(LLM_MODEL),
    messages: window,
  });
  messages.push({ role: "assistant", content: result.text });
  return result.text;
}

console.log(await chat("What is the capital of France?"));
console.log(await chat("What is its population?"));
