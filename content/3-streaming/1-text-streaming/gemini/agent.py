from google import genai

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()

# generate_content_stream instead of generate_content — that's it
for chunk in client.models.generate_content_stream(
    model=LLM_MODEL,
    contents="Explain what an API is in a few sentences.",
):
    print(chunk.text, end="", flush=True)
print()
# An API (Application Programming Interface) is a set of rules and protocols
# that allows different software applications to communicate with each other...
