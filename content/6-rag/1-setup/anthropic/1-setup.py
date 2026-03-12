from pathlib import Path
import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

# ChromaDB is a vector database that stores documents and their embeddings.
# PersistentClient saves the index to disk so agent scripts can query it later.
client = chromadb.PersistentClient(path="./acme_index")

# tell ChromaDB which embedding model to use for indexing and queries.
# without this, it silently downloads an ~80MB local model on first run.
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)

# a collection groups related documents — the embedding function above
# converts text to vectors automatically during add and query operations
collection = client.get_or_create_collection(
    "acme_docs", embedding_function=openai_ef,
)

# load documents from docs.txt — each non-empty line becomes one document.
# in production you'd load real files, DB rows, or API responses instead.
lines = [l for l in Path("docs.txt").read_text().splitlines()
         if l.strip() and not l.startswith("#")]

# upsert inserts new docs or updates existing ones (safe to re-run)
collection.upsert(
    documents=lines,
    ids=[f"doc_{i}" for i in range(len(lines))],
)
print(f"Indexed {len(lines)} documents")
