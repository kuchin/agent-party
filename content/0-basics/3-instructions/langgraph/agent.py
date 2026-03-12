from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

# system_prompt is prepended to every conversation automatically
agent = create_agent(
    model,
    tools=[],
    system_prompt="You are a pirate. Always respond in pirate speak.",
)
result = agent.invoke({
    "messages": [("user", "What is the capital of France?")]
})
print(result["messages"][-1].content)
# "Arrr, Paris be the capital, matey!"
