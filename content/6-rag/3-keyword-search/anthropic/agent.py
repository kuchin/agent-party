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

# the tool schema shapes retrieval: list[str] keywords instead of a free-text query
# the description tells the LLM to decompose questions into specific search terms

def search_by_keywords(keywords: list[str]) -> str:
    """Search the knowledge base using specific keywords.
    Use precise terms, not full questions."""
    print(f"-> call: search_by_keywords({keywords})")
    query = " ".join(keywords)
    results = collection.query(query_texts=[query], n_results=3)
    docs = results["documents"][0]
    print(f"-> result: {len(docs)} docs found")
    return "\n\n".join(docs)

tools = [{
    "name": "search_by_keywords",
    "description": "Search the knowledge base using specific keywords. Use precise terms, not full questions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific search keywords",
            },
        },
        "required": ["keywords"],
    },
}]

messages = [{
    "role": "user",
    "content": "Can I get a refund if I cancel my annual Pro plan after a month?",
}]

# step 1: LLM decomposes question into keywords and calls the tool
response = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
)
# handle all tool_use blocks — the LLM may emit more than one
messages.append({"role": "assistant", "content": response.content})
tool_results = []
for block in response.content:
    if block.type == "tool_use":
        result = search_by_keywords(**block.input)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": result,
        })
messages.append({"role": "user", "content": tool_results})

# step 2: send results back, LLM generates answer
response = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, tools=tools, messages=messages,
)
print(response.content[0].text)
# -> call: search_by_keywords(['refund', 'cancel', 'annual', 'Pro'])
# -> result: 3 docs found
# "Yes — annual plans can be refunded within 30 days of purchase."
