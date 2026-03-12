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

const searchDocs = tool({
  description: "Search the knowledge base for relevant documents",
  inputSchema: z.object({ query: z.string() }),
  execute: async ({ query }) => {
    console.log(`-> call: searchDocs(${JSON.stringify(query)})`);
    const results = await index.queryItems(await embed(query), 3);
    const docs = results.map((r) => r.item.metadata.text);
    console.log(`-> result: ${docs.length} docs found`);
    return docs.join("\n\n");
  },
});

const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  tools: { searchDocs },
});

const result = await agent.generate({
  prompt: "What's included in the Pro plan?",
});
console.log(result.text);
// -> call: searchDocs("Pro plan features")
// -> result: 3 docs found
// "The Pro plan costs $49/month and includes priority support,
//  API access, 100GB storage, and up to 10 team members."
