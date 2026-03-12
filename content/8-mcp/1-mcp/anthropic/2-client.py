# MCP client — Anthropic with standard MCP Python client.
#
# Anthropic's Messages API has beta MCP support (mcp_servers param), but it
# requires a publicly-reachable server URL — Anthropic's servers connect to
# yours. For local/stdio transport we use the standard MCP client instead:
# discover tools, convert schemas to Anthropic format, and run the tool loop.
#
# The client starts the MCP server as a subprocess (stdio transport).

import asyncio
import json
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

LLM_MODEL = "claude-sonnet-4-20250514"

client = anthropic.AsyncAnthropic()

server = StdioServerParameters(command="uv", args=["run", "server.py"])


async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from the MCP server and convert to Anthropic format.
            # Anthropic uses "input_schema" instead of OpenAI's "parameters".
            mcp_tools = await session.list_tools()
            tools = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.inputSchema,
                }
                for t in mcp_tools.tools
            ]

            messages = [
                {"role": "user", "content": "Who's the engineering manager and what's their email?"}
            ]

            # Agentic loop — keep calling the LLM until it stops requesting tools.
            while True:
                response = await client.messages.create(
                    model=LLM_MODEL, max_tokens=1024, messages=messages, tools=tools,
                )

                if response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            result = await session.call_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text,
                            })
                    messages.append({"role": "user", "content": tool_results})
                else:
                    print(response.content[-1].text)
                    break


asyncio.run(main())
# -> list_employees("engineering")   -> Alice Chen (E001), Bob Smith, Carol Wu
# -> get_employee("E001")            -> alice@company.com
# "The engineering manager is Alice Chen. Her email is alice@company.com."
