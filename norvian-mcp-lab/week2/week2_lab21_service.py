from week2_lab21_models import (
    CustomerProfile,
    CustomerPolicies,
    Policy
)


class CustomerNotFoundError(Exception):
    pass

CUSTOMERS = {
    "CUST-001": CustomerProfile(
        customer_id="CUST-001",
        full_name="Alice Martin",
        status="ACTIVE"
    ),
    "CUST-002": CustomerProfile(
        customer_id="CUST-002",
        full_name="Marc Tremblay",
        status="INACTIVE"
    )
}

POLICIES = {
    "CUST-001":[
        Policy(
            policy_id="POL-001",
            policy_type="AUTO",
            status="ACTIVE"
        ),
        Policy(
            policy_id="POL-002",
            policy_type="HOME",
            status="CANCELED"
        )
    ],
    "CUST-002":[]
}

def get_customer(customer_id:str) -> CustomerProfile:

    customer = CUSTOMERS.get(customer_id)

    if customer is None:
        raise CustomerNotFoundError(
            f"Customer with id {customer_id} not found"
        )

    return customer

def get_policies(customer_id: str, status: str = "ALL") -> CustomerPolicies:

    get_customer(customer_id)

    policies = POLICIES.get(customer_id, [])
    print(policies)
    if policies != None:
        if status != "ALL" and policies is not None:
            policies = [
                policy
                for policy in policies
                if policy.status == status
            ]

    return CustomerPolicies(
        customer_id=customer_id,
        policies=policies
    )
