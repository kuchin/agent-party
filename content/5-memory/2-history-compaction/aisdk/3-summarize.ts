import { generateText, pruneMessages, type ModelMessage } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";
const SUMMARY_MODEL = "gpt-5-mini"; // cheap model for summaries

// summarization: prune tool/reasoning bloat, then compress old messages
// pruneMessages is built-in (strips tool calls and reasoning content)
// LLM summarization is manual — uses a cheap model for compression
const messages: ModelMessage[] = [];

async function compactHistory(msgs: ModelMessage[]): Promise<ModelMessage[]> {
  // step 1: strip old tool calls and reasoning — built-in, zero-cost
  const pruned = pruneMessages({
    messages: msgs,
    reasoning: "before-last-message",
    toolCalls: "before-last-2-messages",
  });
  if (pruned.length <= 20) return pruned;
  // step 2: still too long — summarize older messages with a cheap model
  const old = pruned.slice(0, -10);
  const recent = pruned.slice(-10);
  const { text } = await generateText({
    model: openai(SUMMARY_MODEL),
    messages: [
      {
        role: "user",
        content:
          "Summarize this conversation in 2-3 sentences. " +
          `Preserve key facts and decisions.\n\n${JSON.stringify(old)}`,
      },
    ],
  });
  return [{ role: "assistant", content: `[Summary]: ${text}` }, ...recent];
}

async function chat(message: string): Promise<string> {
  messages.push({ role: "user", content: message });
  const compacted = await compactHistory(messages);
  const result = await generateText({
    model: openai(LLM_MODEL),
    messages: compacted,
  });
  messages.push({ role: "assistant", content: result.text });
  return result.text;
}

console.log(await chat("What is the capital of France?"));
console.log(await chat("What is its population?"));
