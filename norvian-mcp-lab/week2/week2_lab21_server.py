from typing import Annotated, Literal

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from week2_lab21_models import (
    CustomerProfile, 
    CustomerPolicies
)

from week2_lab21_service import (
    get_customer,
    get_policies
)

mcp = MCPServer(
    title="Customer Management Service",
    description="A simple service to manage customers and their policies",
    version="0.1.0"
)

CustomerId = Annotated[
    str,
    Field(
        pattern=r"^CUST-[0-9]{3}$",
        description=(
            "The unique identifier of the customer"
            "Example: CUST-001"
        )
    )
]

@mcp.tool(
    title="Get Customer Profile",
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=True
    )
)
def get_customer_profile(
    customer_id: CustomerId
) -> CustomerProfile:
    """
    Get the profile of a customer by their unique identifier.

    Args:
        customer_id (str): The unique identifier of the customer.

    Returns:
        CustomerProfile: The profile of the customer.
    """

    return get_customer(customer_id)

@mcp.tool(
    title="Get Customer Policies",
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=True
    )
)
def list_customer_policies(
    customer_id: CustomerId,
    status: Annotated[
        Literal["ALL","ACTIVE","CANCELLED"],
        Field(
            description=(
                "The status of the policies to filter by."
                "If not provided, all policies will be returned."
            )
        )
    ] = "ALL"
) -> CustomerPolicies:
    """
    Get the policies of a customer by their unique identifier.

    Args:
        customer_id (str): The unique identifier of the customer.

    Returns:
        CustomerPolicies: The policies of the customer.
    """
    return get_policies(customer_id, status)

if __name__ == "__main__":
    mcp.run(transport="stdio")