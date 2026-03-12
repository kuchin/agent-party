# MCP client — LangGraph with langchain-mcp-adapters.
#
# LangGraph uses langchain-mcp-adapters to bridge MCP and LangChain.
# load_mcp_tools() converts MCP tool schemas into LangChain BaseTool
# objects — after that, the agent works exactly like any other LangGraph agent.
#
# The client starts the MCP server as a subprocess (stdio transport).

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

# StdioServerParameters configures the subprocess — same MCP server,
# but launched as a child process instead of over HTTP.
# stdio_client handles the JSON-RPC protocol over stdin/stdout.

server = StdioServerParameters(command="uv", args=["run", "server.py"])

async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Convert MCP tools into LangChain tools. From here on,
            # the agent doesn't know or care they came from MCP.
            tools = await load_mcp_tools(session)

            agent = create_agent(ChatOpenAI(model=LLM_MODEL), tools)
            result = await agent.ainvoke({
                "messages": "Who's the engineering manager and what's their email?",
            })
            print(result["messages"][-1].content)

asyncio.run(main())
# -> list_employees("engineering")   → Alice Chen (E001), Bob Smith, Carol Wu
# -> get_employee("E001")            → alice@company.com
# "The engineering manager is Alice Chen. Her email is alice@company.com."
