from openai import OpenAI

LLM_MODEL = "gpt-5.4"
SUMMARY_MODEL = "gpt-5-mini"  # cheap model for summaries
client = OpenAI()

# explicit compaction via previous_response_id
# builds server-side conversation state, then compacts it on demand
# gives full control over when compaction happens — call between turns

# turn 1 — kick off the conversation
response = client.responses.create(
    model=LLM_MODEL,
    input="What is the capital of France?",
)
print(response.output_text)
# "The capital of France is Paris."

# turn 2 — previous_response_id chains the conversation server-side
response = client.responses.create(
    model=LLM_MODEL,
    previous_response_id=response.id,
    input=[{"role": "user", "content": "What is its population?"}],
)
print(response.output_text)
# "Approximately 2.1 million in the city proper."

# compact — model compresses the full thread into a shorter context
compacted = client.responses.compact(
    model=SUMMARY_MODEL,
    previous_response_id=response.id,
)

# normalize compacted output to plain dicts before the next call
# avoids PydanticSerializationUnexpectedValue warnings from the SDK
context = []
for item in compacted.output:
    if item.type == "message":
        context.append({"role": item.role, "content": item.content[0].text})
    else:
        context.append(item.model_dump(exclude_unset=True))

# continue with compacted context — old turns are summarized, not lost
response = client.responses.create(
    model=LLM_MODEL,
    input=[
        *context,
        {"role": "user", "content": "And the metro area?"},
    ],
)
print(response.output_text)
