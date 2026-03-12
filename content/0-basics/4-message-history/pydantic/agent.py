from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"
agent = Agent(LLM_MODEL)

# turn 1
result = agent.run_sync("What is the capital of France?")
print(result.output)
# "The capital of France is Paris."

# without history, the model can't resolve "its"
no_context = agent.run_sync("What is its population?")
print(no_context.output)
# "Could you clarify what 'its' refers to?"

# new_messages() carries the full exchange so "its" resolves to France
result = agent.run_sync("What is its population?", message_history=result.new_messages())
print(result.output)
# "The population of Paris is approximately 2.1 million..."
