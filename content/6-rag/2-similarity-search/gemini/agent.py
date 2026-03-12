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

# automatic function calling: SDK executes the tool and feeds results back
config = types.GenerateContentConfig(tools=[search_docs])

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents="What's included in the Pro plan?",
)
print(response.text)
# -> call: search_docs('Pro plan features')
# -> result: 3 docs found
# "The Pro plan costs $49/month and includes priority support,
#  API access, 100GB storage, and up to 10 team members."
