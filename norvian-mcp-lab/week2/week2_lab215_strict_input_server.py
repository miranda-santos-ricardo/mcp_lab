from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from pydantic import BaseModel, Field, ConfigDict

from week2_lab21_customer_models import CustomerProfile 
from week2_lab21_customer_service import get_customer

class GetCustomerProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: str = Field(
        pattern=r"^CUST-[0-9]{3}$",
        description="Customer ID in CUST-NNN format."
    )

mcp = MCPServer(
    "AIEngineerLearningPath Customer Service MCP Lab",
    version="0.1.0",
    description="A simple customer service for the AI Engineer Learning Path MCP Lab.",
)

@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=False,
    )
)
def get_customer_profile_strict_request(
    request: GetCustomerProfileInput
)-> CustomerProfile:
    """
    Get the profile of a customer by their ID.

    Args:
        request (GetCustomerProfileInput): The input containing the customer ID.

    Returns:
        CustomerProfile: The profile of the customer.
    """

    return get_customer(request.customer_id)

if __name__ == "__main__":
    mcp.run(transport="stdio")