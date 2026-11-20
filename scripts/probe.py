import json
from composio_mcp import MCP

m = MCP()
tools = m.tools()
print("TOOLS:", [t["name"] for t in tools])
for t in tools:
    if t["name"] in ("COMPOSIO_REMOTE_WORKBENCH", "COMPOSIO_MULTI_EXECUTE_TOOL", "COMPOSIO_SEARCH_TOOLS", "COMPOSIO_MANAGE_CONNECTIONS"):
        s = t.get("inputSchema", {})
        print("SCHEMA", t["name"], "props=", list(s.get("properties", {}).keys()), "required=", s.get("required"))
