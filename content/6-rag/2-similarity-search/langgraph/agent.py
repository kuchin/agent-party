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

@tool
def search_docs(query: str) -> str:
    """Search the knowledge base for relevant documents."""
    print(f"-> call: search_docs({query!r})")
    results = collection.query(query_texts=[query], n_results=3)
    docs = results["documents"][0]
    print(f"-> result: {len(docs)} docs found")
    return "\n\n".join(docs)

agent = create_agent(model, [search_docs])
result = agent.invoke({
    "messages": [("user", "What's included in the Pro plan?")]
})
print(result["messages"][-1].content)
# -> call: search_docs('Pro plan features')
# -> result: 3 docs found
# "The Pro plan costs $49/month and includes priority support,
#  API access, 100GB storage, and up to 10 team members."
