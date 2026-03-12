// MCP client — Mastra with @mastra/mcp.
//
// Mastra has full MCP support — both server (see server.ts) and client.
// MCPClient manages the subprocess lifecycle; listTools() returns
// tools ready for any Mastra agent.
//
// The client starts the MCP server as a subprocess (stdio transport).

import { Agent } from "@mastra/core/agent";
import { MCPClient } from "@mastra/mcp";

const LLM_MODEL = "openai/gpt-5.4";

// MCPClient manages one or more MCP server connections. Each server entry
// specifies how to start the subprocess. listTools() discovers all tools
// across all configured servers.
// Compare with the Tools section where tools were createTool() objects.

const mcp = new MCPClient({
  id: "mcp-client",
  servers: {
    directory: {
      command: "bun",
      args: ["run", "server.ts"],
    },
  },
});

const tools = await mcp.listTools();

const agent = new Agent({
  name: "mcp-agent",
  instructions: "You are a helpful assistant.",
  model: LLM_MODEL,
  tools,
});

const result = await agent.generate(
  "Who's the engineering manager and what's their email?",
  { maxSteps: 5 },
);

console.log(result.text);
await mcp.disconnect();
// -> list_employees("engineering")   → Alice Chen (E001), Bob Smith, Carol Wu
// -> get_employee("E001")            → alice@company.com
// "The engineering manager is Alice Chen. Her email is alice@company.com."
