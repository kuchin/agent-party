import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"

# connect to indexed documents — see Setup scenario
db = chromadb.PersistentClient(path="./acme_index")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)
collection = db.get_collection("acme_docs", embedding_function=openai_ef)

agent = Agent(LLM_MODEL)

# the tool schema shapes retrieval: list[str] keywords instead of a free-text query
# the description tells the LLM to decompose questions into specific search terms

@agent.tool_plain
def search_by_keywords(keywords: list[str]) -> str:
    """Search the knowledge base using specific keywords.
    Use precise terms, not full questions."""
    print(f"-> call: search_by_keywords({keywords})")
    query = " ".join(keywords)
    results = collection.query(query_texts=[query], n_results=3)
    docs = results["documents"][0]
    print(f"-> result: {len(docs)} docs found")
    return "\n\n".join(docs)

result = agent.run_sync(
    "Can I get a refund if I cancel my annual Pro plan after a month?",
)
print(result.output)
# -> call: search_by_keywords(['refund', 'cancel', 'annual', 'Pro'])
# -> result: 3 docs found
# "Yes — annual plans can be refunded within 30 days of purchase."
