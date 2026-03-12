# MCP client — Pydantic AI with first-class MCP support.
#
# Pydantic AI has first-class MCP support. The agent discovers tools when
# the MCP server subprocess starts. No manual tool conversion, no explicit
# session management.
#
# The client starts the MCP server as a subprocess (stdio transport).

import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

LLM_MODEL = "openai:gpt-5.4"

# MCPServerStdio wraps a subprocess. Pass it to toolsets — the agent
# discovers available tools at runtime via the MCP protocol.
# Compare with the Tools section where tools were @agent.tool functions.

server = MCPServerStdio("uv", args=["run", "server.py"])

agent = Agent(LLM_MODEL, toolsets=[server])

async def main():
    async with agent:
        result = await agent.run(
            "Who's the engineering manager and what's their email?",
        )
        print(result.output)

asyncio.run(main())
# -> list_employees("engineering")   → Alice Chen (E001), Bob Smith, Carol Wu
# -> get_employee("E001")            → alice@company.com
# "The engineering manager is Alice Chen. Her email is alice@company.com."
