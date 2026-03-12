# MCP server — a company employee directory exposed as tools.
#
# This server is not framework-specific. It uses the standard MCP Python SDK
# (pip install mcp). Any MCP-compatible agent can connect, discover these tools,
# and call them — without needing this source code.
#
# Compare with the Tools section where tools lived inside the agent's file.
# Here they live on a separate server that ships, deploys, and scales independently.

from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("Company Directory")

# --- Mock data ---

# Department rosters — summary data for browsing
# In production: query from HR database or org-chart API
DEPARTMENTS = {
    "engineering": [
        {"id": "E001", "name": "Alice Chen", "role": "Engineering Manager"},
        {"id": "E002", "name": "Bob Smith", "role": "Senior Developer"},
        {"id": "E003", "name": "Carol Wu", "role": "Developer"},
    ],
    "sales": [
        {"id": "E004", "name": "Diana Ross", "role": "Sales Director"},
        {"id": "E005", "name": "Ethan Kim", "role": "Account Executive"},
    ],
    "design": [
        {"id": "E006", "name": "Frank Lee", "role": "Design Lead"},
    ],
}

# Employee profiles — full records keyed by employee ID
# In production: query from directory service (LDAP, Workday, etc.)
PROFILES = {
    "E001": {"name": "Alice Chen", "email": "alice@company.com", "department": "engineering", "role": "Engineering Manager", "office": "SF-4A"},
    "E002": {"name": "Bob Smith", "email": "bob@company.com", "department": "engineering", "role": "Senior Developer", "office": "SF-4B"},
    "E003": {"name": "Carol Wu", "email": "carol@company.com", "department": "engineering", "role": "Developer", "office": "SF-4C"},
    "E004": {"name": "Diana Ross", "email": "diana@company.com", "department": "sales", "role": "Sales Director", "office": "NY-12A"},
    "E005": {"name": "Ethan Kim", "email": "ethan@company.com", "department": "sales", "role": "Account Executive", "office": "NY-12B"},
    "E006": {"name": "Frank Lee", "email": "frank@company.com", "department": "design", "role": "Design Lead", "office": "SF-5A"},
}


# --- Tools ---
# MCP tools are functions decorated with @mcp.tool(). The SDK extracts
# the function name, docstring, and type hints to build the tool schema
# that clients discover at runtime.

@mcp.tool()
def list_employees(department: str) -> str:
    """List employees in a department. Returns employee IDs, names, and roles."""
    employees = DEPARTMENTS.get(department.lower())
    if not employees:
        available = ", ".join(DEPARTMENTS.keys())
        return f"Unknown department '{department}'. Available: {available}"
    return json.dumps(employees, indent=2)

@mcp.tool()
def get_employee(employee_id: str) -> str:
    """Get full profile for an employee by ID. Returns name, email, department, role, and office."""
    profile = PROFILES.get(employee_id.upper())
    if not profile:
        return f"No employee with ID '{employee_id}'."
    return json.dumps(profile, indent=2)


# stdio transport — the client starts this server as a subprocess.
# stdin/stdout carry the MCP protocol messages (JSON-RPC).
mcp.run()
