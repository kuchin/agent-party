#!/bin/bash
# The client starts the MCP server as a child process via stdio transport.
# stdin/stdout carry the MCP protocol — no network setup needed.
bun run client.ts
