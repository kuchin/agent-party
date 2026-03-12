import { ToolLoopAgent, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { LocalIndex } from "vectra";
import OpenAI from "openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

// connect to indexed documents — see Setup scenario
const index = new LocalIndex("./acme_index");
const embeddingClient = new OpenAI();

async function embed(text: string) {
  const r = await embeddingClient.embeddings.create({
    model: "text-embedding-3-small",
    input: text,
  });
  return r.data[0].embedding;
}

// the tool schema shapes retrieval: string[] keywords instead of a free-text query
// the description tells the LLM to decompose questions into specific search terms

const searchByKeywords = tool({
  description:
    "Search the knowledge base using specific keywords. Use precise terms, not full questions.",
  inputSchema: z.object({
    keywords: z.array(z.string()).describe("Specific search keywords"),
  }),
  execute: async ({ keywords }) => {
    console.log(`-> call: searchByKeywords(${JSON.stringify(keywords)})`);
    const results = await index.queryItems(
      await embed(keywords.join(" ")),
      3,
    );
    const docs = results.map((r) => r.item.metadata.text);
    console.log(`-> result: ${docs.length} docs found`);
    return docs.join("\n\n");
  },
});

const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  tools: { searchByKeywords },
});

const result = await agent.generate({
  prompt: "Can I get a refund if I cancel my annual Pro plan after a month?",
});
console.log(result.text);
// -> call: searchByKeywords(["refund", "cancel", "annual", "Pro"])
// -> result: 3 docs found
// "Yes — annual plans can be refunded within 30 days of purchase."
