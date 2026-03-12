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

input = [{"role": "user", "content": "What's included in the Pro plan?"}]

# step 1: LLM calls the search tool
response = client.responses.create(
    model=LLM_MODEL, input=input, tools=tools,
)
tool_call = next(i for i in response.output if i.type == "function_call")
result = search_docs(**json.loads(tool_call.arguments))

# step 2: send results back, LLM generates answer
input += response.output
input.append({
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": result,
})

response = client.responses.create(
    model=LLM_MODEL, input=input, tools=tools,
)
print(response.output_text)
# -> call: search_docs('Pro plan features')
# -> result: 3 docs found
# "The Pro plan costs $49/month and includes priority support,
#  API access, 100GB storage, and up to 10 team members."
