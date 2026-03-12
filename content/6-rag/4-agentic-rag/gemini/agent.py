import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# connect to indexed documents — see Setup scenario
db = chromadb.PersistentClient(path="./acme_index")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)
collection = db.get_collection("acme_docs", embedding_function=openai_ef)

def search_docs(query: str) -> str:
    """Search the knowledge base for relevant documents."""
    print(f"-> call: search_docs({query!r})")
    results = collection.query(query_texts=[query], n_results=3)
    docs = results["documents"][0]
    print(f"-> result: {len(docs)} docs found")
    return "\n\n".join(docs)

# automatic function calling: SDK runs the multi-step ReAct loop
config = types.GenerateContentConfig(
    tools=[search_docs],
    system_instruction=(
        "You are a support agent. Search the knowledge base to answer questions. "
        "If results don't fully answer the question, search again with different terms."
    ),
)

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents=(
        "I'm choosing between Pro and Enterprise. I need SSO and at least "
        "99.9% uptime. Which plan should I pick and what's the price difference?"
    ),
)
print(response.text)
# -> call: search_docs('SSO uptime Pro Enterprise')
# -> result: 3 docs found
# -> call: search_docs('Pro Enterprise pricing comparison')
# -> result: 3 docs found
# "Based on your requirements ... Enterprise plan at $199/month."
