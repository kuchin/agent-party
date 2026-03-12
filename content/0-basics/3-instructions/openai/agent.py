from openai import OpenAI

LLM_MODEL = "gpt-5.4"

client = OpenAI()

# instructions is sent as a system message before the input
response = client.responses.create(
    model=LLM_MODEL,
    instructions="You are a pirate. Always respond in pirate speak.",
    input="What is the capital of France?",
)
print(response.output_text)
# "Arrr, Paris be the capital, matey!"
