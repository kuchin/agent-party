from openai import OpenAI

LLM_MODEL = "gpt-5.4"

client = OpenAI()

response = client.responses.create(
    model=LLM_MODEL,
    input="What is the capital of France?",
)
print(response.output_text)
# "Paris."
