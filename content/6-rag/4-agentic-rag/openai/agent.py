import json
import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from openai import OpenAI

LLM_MODEL = "gpt-5.4"
client = OpenAI()

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

tools = [{
    "type": "function",
    "name": "search_docs",
    "description": "Search the knowledge base for relevant documents.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
        },
        "required": ["query"],
    },
}]

input = [
    {"role": "developer", "content": (
        "You are a support agent. Search the knowledge base to answer questions. "
        "If results don't fully answer the question, search again with different terms."
    )},
    {"role": "user", "content": (
        "I'm choosing between Pro and Enterprise. I need SSO and at least "
        "99.9% uptime. Which plan should I pick and what's the price difference?"
    )},
]

# agentic loop: LLM searches multiple times until it has enough info
while True:
    response = client.responses.create(
        model=LLM_MODEL, input=input, tools=tools,
    )
    tool_calls = [i for i in response.output if i.type == "function_call"]
    if not tool_calls:
        break
    input += response.output
    for tc in tool_calls:
        result = search_docs(**json.loads(tc.arguments))
        input.append({
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": result,
        })

print(response.output_text)
# -> call: search_docs('SSO uptime Pro Enterprise')
# -> result: 3 docs found
# -> call: search_docs('Pro Enterprise pricing comparison')
# -> result: 3 docs found
# "Based on your requirements ... Enterprise plan at $199/month."
