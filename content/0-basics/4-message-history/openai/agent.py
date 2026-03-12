from openai import OpenAI

LLM_MODEL = "gpt-5.4"
client = OpenAI()

# turn 1
messages = [{"role": "user", "content": "What is the capital of France?"}]
response = client.responses.create(model=LLM_MODEL, input=messages)
print(response.output_text)
# "The capital of France is Paris."

# without history, the model can't resolve "its"
no_context = client.responses.create(model=LLM_MODEL, input="What is its population?")
print(no_context.output_text)
# "Could you clarify what 'its' refers to?"

# the API is stateless — pass the full conversation each call
messages += response.output
messages.append({"role": "user", "content": "What is its population?"})

response = client.responses.create(model=LLM_MODEL, input=messages)
print(response.output_text)
# "The population of Paris is approximately 2.1 million..."
