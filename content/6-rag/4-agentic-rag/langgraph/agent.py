import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

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

# invoke handles the multi-step loop automatically
agent = create_agent(model, [search_docs])
result = agent.invoke({
    "messages": [
        SystemMessage(content=(
            "You are a support agent. Search the knowledge base to answer questions. "
            "If results don't fully answer the question, search again with different terms."
        )),
        ("user", (
            "I'm choosing between Pro and Enterprise. I need SSO and at least "
            "99.9% uptime. Which plan should I pick and what's the price difference?"
        )),
    ]
})
print(result["messages"][-1].content)
# -> call: search_docs('SSO uptime Pro Enterprise')
# -> result: 3 docs found
# -> call: search_docs('Pro Enterprise pricing comparison')
# -> result: 3 docs found
# "Based on your requirements ... Enterprise plan at $199/month."
