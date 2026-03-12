# MCP client — Gemini with MCP session passed directly as a tool.
#
# Gemini's unique approach: pass the MCP ClientSession directly as a tool.
# The SDK extracts tool schemas and handles calling internally.
# No manual conversion needed.
#
# The client starts the MCP server as a subprocess (stdio transport).

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

LLM_MODEL = "gemini-2.5-flash"

# stdio_client manages the MCP subprocess. ClientSession handles the JSON-RPC
# protocol. The session is passed directly to Gemini as a tool — the SDK
# discovers tool schemas and handles calling automatically.
# Compare with the Tools section where tools were plain Python functions.

server = StdioServerParameters(command="uv", args=["run", "server.py"])

client = genai.Client()

async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            response = await client.aio.models.generate_content(
                model=LLM_MODEL,
                contents="Who's the engineering manager and what's their email?",
                config=genai.types.GenerateContentConfig(
                    tools=[session],
                ),
            )
            print(response.text)

asyncio.run(main())
# -> list_employees("engineering")   → Alice Chen (E001), Bob Smith, Carol Wu
# -> get_employee("E001")            → alice@company.com
# "The engineering manager is Alice Chen. Her email is alice@company.com."
