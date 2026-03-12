from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# turn 1
contents = [types.Content(role="user", parts=[types.Part.from_text(text="What is the capital of France?")])]
response = client.models.generate_content(model=LLM_MODEL, contents=contents)
print(response.text)
# "The capital of France is Paris."

# without history, the model can't resolve "its"
no_context = client.models.generate_content(model=LLM_MODEL, contents="What is its population?")
print(no_context.text)
# "Could you clarify what 'its' refers to?"

# the API is stateless — pass the full conversation each call
contents.append(response.candidates[0].content)
contents.append(types.Content(role="user", parts=[types.Part.from_text(text="What is its population?")]))

response = client.models.generate_content(model=LLM_MODEL, contents=contents)
print(response.text)
# "The population of Paris is approximately 2.1 million..."
