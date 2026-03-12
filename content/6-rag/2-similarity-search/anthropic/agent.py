import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

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
    "name": "search_docs",
    "description": "Search the knowledge base for relevant documents.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
        },
        "required": ["query"],
    },
}]

messages = [{"role": "user", "content": "What's included in the Pro plan?"}]

# step 1: LLM calls the search tool
response = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
)
tool_block = next(b for b in response.content if b.type == "tool_use")
result = search_docs(**tool_block.input)

# step 2: send results back, LLM generates answer
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": [{
    "type": "tool_result",
    "tool_use_id": tool_block.id,
    "content": result,
}]})

response = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
)
print(response.content[0].text)
# -> call: search_docs('Pro plan features')
# -> result: 3 docs found
# "The Pro plan costs $49/month and includes priority support,
#  API access, 100GB storage, and up to 10 team members."
