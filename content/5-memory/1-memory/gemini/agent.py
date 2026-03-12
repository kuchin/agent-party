from google import genai

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# chat session manages history — just send the next message
chat = client.chats.create(model=LLM_MODEL)

# turn 1
response = chat.send_message("What is the capital of France?")
print(response.text)
# "The capital of France is Paris."

# turn 2 — chat session remembers the conversation
response = chat.send_message("What is its population?")
print(response.text)
# "The population of Paris is approximately 2.1 million..."
