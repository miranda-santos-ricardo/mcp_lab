from typing import Annotated, Literal

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from week2_lab21_customer_models import (
    CustomerProfile,
    CustomerPolicies,
    Policy,
    GetCustomerProfileInput
)

from week2_lab21_customer_service import (
    get_customer,
    get_customer_policies,
    CustomerNotFoundError
)

mcp = MCPServer("MASTERING customer MCP Server",version="0.1.0")

CustomerId = Annotated[
    str,
    Field(
        pattern=r"^CUST-[0-9]{3}$",
        description="Customer ID in the format CUST-XXX"
    )
]

@mcp.tool(
    title="Get Customer Profile",
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=True
    )
)
def get_customer_profile(customer: GetCustomerProfileInput) -> CustomerProfile:
    """
    Get the profile of a customer by their ID.

    Args:
        customer (GetCustomerProfileInput): The input containing the customer ID.

    Returns:
        CustomerProfile: The profile of the customer.

    Raises:
        CustomerNotFoundError: If the customer with the given ID is not found.
    """
    return get_customer(customer.customer_id)


@mcp.tool(
    title="List Customer Policies",
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def list_customer_policies(
    customer_id: CustomerId,
    status: Annotated[
        Literal["ACTIVE", "CANCELLED", "ALL"],
        Field(
            description="Filter policies by status."
        ),
    ] = "ALL",
) -> CustomerPolicies:
    """List insurance policies for one customer.

    Can filter by ACTIVE or CANCELLED status.
    Returns an empty list if no policies match.
    Never modifies or cancels policies.
    """
    return get_customer_policies(customer_id, status)


if __name__ == "__main__":
    mcp.run(transport="stdio")