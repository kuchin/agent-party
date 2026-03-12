from google import genai

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()

response = client.models.generate_content(
    model=LLM_MODEL,
    contents="What is the capital of France?",
)
print(response.text)
# "Paris."
