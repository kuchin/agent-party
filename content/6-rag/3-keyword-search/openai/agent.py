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
    "type": "function",
    "name": "search_by_keywords",
    "description": "Search the knowledge base using specific keywords. Use precise terms, not full questions.",
    "parameters": {
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

input = [{
    "role": "user",
    "content": "Can I get a refund if I cancel my annual Pro plan after a month?",
}]

# step 1: LLM decomposes question into keywords and calls the tool
response = client.responses.create(
    model=LLM_MODEL, input=input, tools=tools,
)
# handle all tool calls — the LLM may emit more than one
input += response.output
for item in response.output:
    if item.type == "function_call":
        result = search_by_keywords(**json.loads(item.arguments))
        input.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": result,
        })

# step 2: send results back, LLM generates answer
response = client.responses.create(
    model=LLM_MODEL, input=input, tools=tools,
)
print(response.output_text)
# -> call: search_by_keywords(['refund', 'cancel', 'annual', 'Pro'])
# -> result: 3 docs found
# "Yes — annual plans can be refunded within 30 days of purchase."
