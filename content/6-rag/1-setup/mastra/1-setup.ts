import { LocalIndex } from "vectra";
import { readFileSync } from "fs";
import OpenAI from "openai";

// Vectra is a local vector database that stores documents with their embeddings.
// Unlike ChromaDB (Python), Vectra requires you to compute embeddings yourself —
// we use OpenAI's embedding model for that.
const openai = new OpenAI();

// LocalIndex persists to disk so agent scripts can query it later
const index = new LocalIndex("./acme_index");
if (!(await index.isIndexCreated())) await index.createIndex();

// load documents from docs.txt — each non-empty line becomes one document.
// in production you'd load real files, DB rows, or API responses instead.
const lines = readFileSync("docs.txt", "utf-8")
  .split("\n")
  .filter((l) => l.trim() && !l.startsWith("#"));

// embed each document and store it in the index
for (const [i, doc] of lines.entries()) {
  const res = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: doc,
  });
  await index.insertItem({
    id: `doc_${i}`,
    metadata: { text: doc },
    vector: res.data[0].embedding,
  });
}
console.log(`Indexed ${lines.length} documents`);
