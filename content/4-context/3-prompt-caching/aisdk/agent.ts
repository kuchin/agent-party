import { readFileSync } from "fs";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

// prompt caching is automatic with OpenAI — no providerOptions needed
// identical prefixes >= 1024 tokens are cached and reused
// static content (instructions, examples) should go first for best hit rate

const KNOWLEDGE_BASE = readFileSync("knowledge_base.txt", "utf-8"); // ~4100 tokens

// request 1: cold cache — prompt is processed and cached automatically
const r1 = await generateText({
  model: openai(LLM_MODEL),
  system: KNOWLEDGE_BASE,
  prompt: "I keep getting 429 errors. What should I do?",
});
console.log(r1.text);
console.log(`Cached tokens: ${r1.usage.cachedInputTokens ?? 0}`);
// -> Cached tokens: 0 (cache miss — prefix is now stored)

// request 2: warm cache — identical prefix served from cache
const r2 = await generateText({
  model: openai(LLM_MODEL),
  system: KNOWLEDGE_BASE,
  prompt: "How do I fix SSO login failures?",
});
console.log(r2.text);
console.log(`Cached tokens: ${r2.usage.cachedInputTokens ?? 0}`);
// -> Cached tokens: 3200 (cache hit — lower cost, lower latency)
