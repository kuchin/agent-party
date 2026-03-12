# MCP client — OpenAI with standard MCP Python client.
#
# OpenAI's Responses API has built-in MCP support (type: "mcp"), but it
# requires a publicly-reachable server URL — OpenAI's servers connect to
# yours. For local/stdio transport we use the standard MCP client instead:
# discover tools, convert schemas to OpenAI format, and run the tool loop.
#
# The client starts the MCP server as a subprocess (stdio transport).

import asyncio
import json
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

LLM_MODEL = "gpt-5.4"

client = AsyncOpenAI()

server = StdioServerParameters(command="uv", args=["run", "server.py"])


async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from the MCP server and convert to OpenAI format.
            # MCP tool schemas are JSON Schema — same format OpenAI expects.
            mcp_tools = await session.list_tools()
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or "",
                        "parameters": t.inputSchema,
                    },
                }
                for t in mcp_tools.tools
            ]

            messages = [
                {"role": "user", "content": "Who's the engineering manager and what's their email?"}
            ]

            # Agentic loop — keep calling the LLM until it stops requesting tools.
            while True:
                response = await client.chat.completions.create(
                    model=LLM_MODEL, messages=messages, tools=tools,
                )
                choice = response.choices[0]

                if choice.finish_reason == "tool_calls":
                    messages.append(choice.message)
                    for tc in choice.message.tool_calls:
                        result = await session.call_tool(
                            tc.function.name, json.loads(tc.function.arguments),
                        )
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result.content[0].text,
                        })
                else:
                    print(choice.message.content)
                    break


asyncio.run(main())
# -> list_employees("engineering")   -> Alice Chen (E001), Bob Smith, Carol Wu
# -> get_employee("E001")            -> alice@company.com
# "The engineering manager is Alice Chen. Her email is alice@company.com."
