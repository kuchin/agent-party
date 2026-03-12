from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
SUMMARY_MODEL = "gemini-flash-latest"  # cheap model for summaries
client = genai.Client()

# summarization: compress old messages with a cheap model
# no built-in compaction API — call a fast model to summarize,
# then replace old messages with the summary
WINDOW = 10
history: list[types.Content] = []

def summarize_old(messages: list[types.Content]) -> list[types.Content]:
    if len(messages) <= 20:
        return messages  # short enough — no compression needed
    old, recent = messages[:-WINDOW], messages[-WINDOW:]
    summary = client.models.generate_content(
        model=SUMMARY_MODEL,
        contents=[
            types.Content(role="user", parts=[types.Part(
                text=f"Summarize this conversation in 2-3 sentences. "
                f"Preserve key facts and decisions.\n\n{old}",
            )]),
        ],
    )
    return [
        types.Content(role="user", parts=[types.Part(
            text=f"[Summary of earlier conversation]: {summary.text}",
        )]),
        *recent,
    ]

def chat(message: str) -> str:
    history.append(types.Content(role="user", parts=[types.Part(text=message)]))
    window = summarize_old(history)
    response = client.models.generate_content(
        model=LLM_MODEL, contents=window,
    )
    history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
    return response.text

print(chat("What is the capital of France?"))
print(chat("What is its population?"))
