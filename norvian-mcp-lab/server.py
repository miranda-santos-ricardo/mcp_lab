from mcp.server import MCPServer

mcp = MCPServer("Norvian MCP Lab")

TOOLS = {
    "document.search": "LOW",
    "customer.read": "MEDIUM",
    "payment.execute": "HIGH",
}

@mcp.tool()
def get_nada():
    """
    A tool that does nothing.
    """
    return "Nothing to see here."

@mcp.tool()
def get_tool_risk(tool_name: str) -> dict:
    """
    Get the risk level of a tool.

    Args:
        tool_name (str): The name of the tool.

    Returns:
        dict: A dictionary containing the tool name and its risk level.
    """

    risk = TOOLS.get(tool_name, "UNKNOWN")

    if risk is None:
        return {
            "found": False,
            "tool_name": tool_name,
            "risk_level": "UNKNOWN"
        }
    
    return {
        "found": True,
        "tool_name": tool_name,
        "risk_level": risk
    }

@mcp.resource("norvian://policies/risk-levels")
def risk_policy() -> str:
    """
    Describr tool risk classifications and their associated risk levels.
    """
    return (
        "Low: read-only applications",
        "MEDIUM: access to sensitive data",
        "HIGH: operations with significant side effects"
    )
