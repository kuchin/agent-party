import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)

# connect to indexed documents — see Setup scenario
db = chromadb.PersistentClient(path="./acme_index")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)
collection = db.get_collection("acme_docs", embedding_function=openai_ef)

# the tool schema shapes retrieval: list[str] keywords instead of a free-text query
# the description tells the LLM to decompose questions into specific search terms

@tool
def search_by_keywords(keywords: list[str]) -> str:
    """Search the knowledge base using specific keywords.
    Use precise terms, not full questions."""
    print(f"-> call: search_by_keywords({keywords})")
    query = " ".join(keywords)
    results = collection.query(query_texts=[query], n_results=3)
    docs = results["documents"][0]
    print(f"-> result: {len(docs)} docs found")
    return "\n\n".join(docs)

agent = create_agent(model, [search_by_keywords])
result = agent.invoke({
    "messages": [(
        "user",
        "Can I get a refund if I cancel my annual Pro plan after a month?",
    )]
})
print(result["messages"][-1].content)
# -> call: search_by_keywords(['refund', 'cancel', 'annual', 'Pro'])
# -> result: 3 docs found
# "Yes — annual plans can be refunded within 30 days of purchase."
