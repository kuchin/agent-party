// MCP server — a company employee directory exposed as tools.
//
// This server is not framework-specific. It uses the standard MCP TypeScript SDK
// (@modelcontextprotocol/sdk). Any MCP-compatible agent can connect, discover
// these tools, and call them — without needing this source code.
//
// Compare with the Tools section where tools lived inside the agent's file.
// Here they live on a separate server that ships, deploys, and scales independently.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// --- Mock data ---

// Department rosters — summary data for browsing
// In production: query from HR database or org-chart API
const DEPARTMENTS: Record<string, { id: string; name: string; role: string }[]> = {
  engineering: [
    { id: "E001", name: "Alice Chen", role: "Engineering Manager" },
    { id: "E002", name: "Bob Smith", role: "Senior Developer" },
    { id: "E003", name: "Carol Wu", role: "Developer" },
  ],
  sales: [
    { id: "E004", name: "Diana Ross", role: "Sales Director" },
    { id: "E005", name: "Ethan Kim", role: "Account Executive" },
  ],
  design: [
    { id: "E006", name: "Frank Lee", role: "Design Lead" },
  ],
};

// Employee profiles — full records keyed by employee ID
// In production: query from directory service (LDAP, Workday, etc.)
const PROFILES: Record<string, { name: string; email: string; department: string; role: string; office: string }> = {
  E001: { name: "Alice Chen", email: "alice@company.com", department: "engineering", role: "Engineering Manager", office: "SF-4A" },
  E002: { name: "Bob Smith", email: "bob@company.com", department: "engineering", role: "Senior Developer", office: "SF-4B" },
  E003: { name: "Carol Wu", email: "carol@company.com", department: "engineering", role: "Developer", office: "SF-4C" },
  E004: { name: "Diana Ross", email: "diana@company.com", department: "sales", role: "Sales Director", office: "NY-12A" },
  E005: { name: "Ethan Kim", email: "ethan@company.com", department: "sales", role: "Account Executive", office: "NY-12B" },
  E006: { name: "Frank Lee", email: "frank@company.com", department: "design", role: "Design Lead", office: "SF-5A" },
};


// --- Server + Tools ---
// McpServer registers tools with typed Zod schemas. The SDK handles
// JSON-RPC protocol, tool discovery, and schema validation automatically.

const server = new McpServer({ name: "Company Directory", version: "1.0.0" });

server.tool(
  "list_employees",
  "List employees in a department. Returns employee IDs, names, and roles.",
  { department: z.string() },
  async ({ department }) => {
    const employees = DEPARTMENTS[department.toLowerCase()];
    if (!employees) {
      const available = Object.keys(DEPARTMENTS).join(", ");
      return { content: [{ type: "text", text: `Unknown department '${department}'. Available: ${available}` }] };
    }
    return { content: [{ type: "text", text: JSON.stringify(employees, null, 2) }] };
  },
);

server.tool(
  "get_employee",
  "Get full profile for an employee by ID. Returns name, email, department, role, and office.",
  { employee_id: z.string() },
  async ({ employee_id }) => {
    const profile = PROFILES[employee_id.toUpperCase()];
    if (!profile) {
      return { content: [{ type: "text", text: `No employee with ID '${employee_id}'.` }] };
    }
    return { content: [{ type: "text", text: JSON.stringify(profile, null, 2) }] };
  },
);


// stdio transport — the client starts this server as a subprocess.
// stdin/stdout carry the MCP protocol messages (JSON-RPC).
const transport = new StdioServerTransport();
await server.connect(transport);
