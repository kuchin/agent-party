from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"

# instructions is the preferred prompt surface for most Pydantic AI agents
agent = Agent(
    LLM_MODEL,
    instructions="You are a pirate. Always respond in pirate speak.",
)
result = agent.run_sync("What is the capital of France?")
print(result.output)
# "Arrr, Paris be the capital, matey!"
