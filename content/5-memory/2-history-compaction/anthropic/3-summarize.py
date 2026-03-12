import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

# compaction with pause: API compacts then pauses so you can inspect
# the summary before continuing — gives full control over the process
# custom instructions guide what the summary should preserve

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
                "pause_after_compaction": True,
                "instructions": "Preserve key facts, decisions, and code snippets.",
            }]
        },
    )
    messages.append({"role": "assistant", "content": response.content})
    # if compaction triggered, stop_reason is "compaction" — resume to continue
    if response.stop_reason == "compaction":
        response = client.beta.messages.create(
            betas=["compact-2026-01-12"],
            model=LLM_MODEL,
            max_tokens=1024,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
    return response.content[0].text

print(chat("What is the capital of France?"))
print(chat("What is its population?"))
