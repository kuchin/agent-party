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

// ToolLoopAgent handles the multi-step loop automatically
const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  system: `\
You are a support agent. Search the knowledge base to answer questions.
If results don't fully answer the question, search again with different terms.
`,
  tools: { searchDocs },
});

const result = await agent.generate({
  prompt: `\
I'm choosing between Pro and Enterprise. I need SSO and at least
99.9% uptime. Which plan should I pick and what's the price difference?
`,
});
console.log(result.text);
// -> call: searchDocs("SSO uptime Pro Enterprise")
// -> result: 3 docs found
// -> call: searchDocs("Pro Enterprise pricing comparison")
// -> result: 3 docs found
// "Based on your requirements ... Enterprise plan at $199/month."
