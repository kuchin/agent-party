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

system = (
    "You are a support agent. Search the knowledge base to answer questions. "
    "If results don't fully answer the question, search again with different terms."
)

messages = [{"role": "user", "content": (
    "I'm choosing between Pro and Enterprise. I need SSO and at least "
    "99.9% uptime. Which plan should I pick and what's the price difference?"
)}]

# agentic loop: LLM searches multiple times until it has enough info
while True:
    response = client.messages.create(
        model=LLM_MODEL, max_tokens=1024,
        system=system, tools=tools, messages=messages,
    )
    if response.stop_reason != "tool_use":
        break
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = search_docs(**block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
    messages.append({"role": "user", "content": tool_results})

print(response.content[0].text)
# -> call: search_docs('SSO uptime Pro Enterprise')
# -> result: 3 docs found
# -> call: search_docs('Pro Enterprise pricing comparison')
# -> result: 3 docs found
# "Based on your requirements ... Enterprise plan at $199/month."
