from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

LLM_MODEL = "gemini-pro-latest"

model = ChatGoogleGenerativeAI(model=LLM_MODEL)

# create_agent builds a graph that loops: LLM → tools → LLM
# with no tools, it's a simple prompt → response
agent = create_agent(model, tools=[])

result = agent.invoke({
    "messages": [("user", "What is the capital of France?")]
})
print(result["messages"][-1].text)
# "Paris."
