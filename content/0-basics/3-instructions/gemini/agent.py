from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()

# system_instruction is passed via GenerateContentConfig
response = client.models.generate_content(
    model=LLM_MODEL,
    config=types.GenerateContentConfig(
        system_instruction="You are a pirate. Always respond in pirate speak.",
    ),
    contents="What is the capital of France?",
)
print(response.text)
# "Arrr, Paris be the capital, matey!"
