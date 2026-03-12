import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

# token-aware compaction: API auto-compacts when input tokens exceed trigger
# replaces old messages with an LLM-generated summary (beta feature)
# on subsequent requests, messages before the compaction block are auto-dropped

messages: list = []

def chat(message: str) -> str:
    messages.append({"role": "user", "content": message})
    response = client.beta.messages.create(
        betas=["compact-2026-01-12"],
        model=LLM_MODEL,
        max_tokens=1024,
        messages=messages,
        context_management={
            "edits": [{
                "type": "compact_20260112",
                "trigger": {"type": "input_tokens", "value": 100_000},
            }]
        },
    )
    # response may include compaction blocks — append as-is
    messages.append({"role": "assistant", "content": response.content})
    return response.content[0].text

print(chat("What is the capital of France?"))
print(chat("What is its population?"))
