from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

# create_agent builds a graph that loops: LLM → tools → LLM
# with no tools, it's a simple prompt → response
agent = create_agent(model, tools=[])

result = agent.invoke({
    "messages": [("user", "What is the capital of France?")]
})
print(result["messages"][-1].content)
# "Paris."
