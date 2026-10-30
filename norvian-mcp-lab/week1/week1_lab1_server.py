from mcp.server import MCPServer

mcp = MCPServer(
    "Norvian Risk Registry MCP Lab",
    version="0.1.0",
    description="A simple risk registry for tools in the Norvian MCP Lab.",
)

TOOLS_REGISTRY = {
    "documents.search":{
        "risk_level": "LOW",
        "requires_approval": False
    },
    "customer.read": {
        "risk_level": "MEDIUM",
        "requires_approval": False
    },
    "payment.execute": {
        "risk_level": "HIGH",
        "requires_approval": True
    },
}

##################################################################
## TOOLS
##################################################################
@mcp.tool()
def get_tool_risk(tool_name: str) -> dict:
    """
    Get the risk level of a tool.

    Args:
        tool_name (str): The name of the tool.

    Returns:
        dict: A dictionary containing the tool name and its risk level.
    """

    entry = TOOLS_REGISTRY.get(tool_name)

    if entry is None:
        return {
            "found": False, 
            "tool_name": tool_name,
            "risk_level": "UNKNOWN",
        }

    return {
        "found": True,
        "tool_name": tool_name,
        **entry,
    }

@mcp.tool()
def list_registered_tools() -> list[str]:
    """
    List all registered tools in the risk registry.

    Returns:
        list[str]: A list of registered tool names.
    """
    return sorted(TOOLS_REGISTRY.keys())

@mcp.tool()
def calculate_purchase_total(
    unit_price: float,
    quantity: int,
) -> dict:
    """Calculate a purchase total without placing an order."""
    if unit_price < 0 or quantity <= 0:
        raise ValueError("Invalid price or quantity")

    return {
        "total": round(unit_price * quantity, 2),
        "currency": "CAD",
    }
##################################################################
## RESOURCES
##################################################################
@mcp.resource("norvian://policies/risk-levels")
def risk_policy() -> str:
    """
    Describe tool risk classifications and their associated risk levels.
    """
    return (
        "LOW: Read-only non-sensitive operations.\n"
        "MEDIUM: Operations involving sensitive information.\n"
        "HIGH: Sensitive operations or significant side effects.\n"
        "Risk classification is not execution authorization."
    )

##################################################################
## PROMPTS
##################################################################
@mcp.prompt()
def review_tool(tool_name:str) -> str:
    """
    Prompt for a review of a tool's risk level.

    Args:
        tool_name (str): The name of the tool to review.
    
    """
    return (
        f"Review the enterprise tool '{tool_name}'."
        "Analyse its risk, potential side effects, "
        "authorization boundaries, and audit requirements."
    )

if __name__ == "__main__":
    mcp.run(transport="stdio")