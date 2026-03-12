from pydantic_ai import Agent

# model specified as "provider:model" string
LLM_MODEL = "openai:gpt-5.4"

agent = Agent(LLM_MODEL)

result = agent.run_sync("What is the capital of France?")
print(result.output)
# "Paris."
