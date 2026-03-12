from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)
agent = create_agent(model, tools=[])

# turn 1
result = agent.invoke({"messages": [("user", "What is the capital of France?")]})
print(result["messages"][-1].content)
# "The capital of France is Paris."

# without history, the model can't resolve "its"
no_context = agent.invoke({"messages": [("user", "What is its population?")]})
print(no_context["messages"][-1].content)
# "Could you clarify what 'its' refers to?"

# the agent is stateless — pass the full conversation each call
result = agent.invoke({"messages": result["messages"] + [("user", "What is its population?")]})
print(result["messages"][-1].content)
# "The population of Paris is approximately 2.1 million..."
