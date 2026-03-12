import asyncio
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

# The graph definition stays exactly the same.
# Async only changes the call site: use ainvoke/astream when the agent runs
# inside an existing event loop or alongside other async work.
agent = create_agent(model, tools=[])


async def main():
    result = await agent.ainvoke({
        "messages": [("user", "What is the capital of France?")]
    })
    print(result["messages"][-1].content)


asyncio.run(main())
# "Paris."
