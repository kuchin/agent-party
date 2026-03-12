// MCP client — AI SDK with @ai-sdk/mcp.
//
// The @ai-sdk/mcp package bridges MCP and the AI SDK. client.tools()
// converts MCP tool schemas into AI SDK tool objects, which plug
// directly into generateText().
//
// The client starts the MCP server as a subprocess (stdio transport).

import { createMCPClient } from "@ai-sdk/mcp";
import { Experimental_StdioMCPTransport as StdioTransport } from "@ai-sdk/mcp/mcp-stdio";
import { generateText, stepCountIs } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

// createMCPClient connects to the server, discovers tools, and returns
// an object whose .tools() method produces AI SDK-compatible tool objects.
// Compare with the Tools section where tools were defined inline with zod schemas.

const client = await createMCPClient({
  transport: new StdioTransport({
    command: "bun",
    args: ["run", "server.ts"],
  }),
});

const result = await generateText({
  model: openai(LLM_MODEL),
  prompt: "Who's the engineering manager and what's their email?",
  tools: await client.tools(),
  stopWhen: stepCountIs(5),
});

console.log(result.text);
await client.close();
// -> list_employees("engineering")   → Alice Chen (E001), Bob Smith, Carol Wu
// -> get_employee("E001")            → alice@company.com
// "The engineering manager is Alice Chen. Her email is alice@company.com."
