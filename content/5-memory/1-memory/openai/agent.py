from openai import OpenAI

LLM_MODEL = "gpt-5.4"
client = OpenAI()

# turn 1
response = client.responses.create(
    model=LLM_MODEL,
    input="What is the capital of France?",
)
print(response.output_text)
# "The capital of France is Paris."

# turn 2 — previous_response_id continues the conversation server-side
response = client.responses.create(
    model=LLM_MODEL,
    previous_response_id=response.id,
    input=[{"role": "user", "content": "What is its population?"}],
)
print(response.output_text)
# "The population of Paris is approximately 2.1 million..."
