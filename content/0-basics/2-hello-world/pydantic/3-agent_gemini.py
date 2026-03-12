from pydantic_ai import Agent

# model specified as "provider:model" string
LLM_MODEL = "google-gla:gemini-pro-latest"

agent = Agent(LLM_MODEL)

result = agent.run_sync("What is the capital of France?")
print(result.output)
# "Paris."
