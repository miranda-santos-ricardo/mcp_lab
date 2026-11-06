import json
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError
)

class Policy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: str = Field(
        pattern=r"^POL-[0-9]{3}$"
    )

    policy_type: Literal["AUTO", "HOME", "LIFE"]
    status: Literal["ACTIVE","CANCELLED"]

class CustomerPolicies(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(
        pattern=r"^CUST-[0-9]{3}$"
    )

    policies: list[Policy]

print("\n ===GENERATED OUTPUT SCHEMA ===")

schema = CustomerPolicies.model_json_schema()
print(json.dumps(schema, indent=2))

test_cases = [
    (
        "VALID WITH POLICIES",
        {
            "customer_id": "CUST-001",
            "policies": [
                {
                    "policy_id": "POL-001",
                    "policy_type": "AUTO",
                    "status": "ACTIVE",
                }
            ],
        },
    ),
    (
        "VALID EMPTY LIST",
        {
            "customer_id": "CUST-001",
            "policies": [],
        },
    ),
    (
        "INVALID NULL",
        {
            "customer_id": "CUST-001",
            "policies": None,
        },
    ),
    (
        "MISSING POLICIES",
        {
            "customer_id": "CUST-001",
        },
    ),
    (
        "INVALID ENUM",
        {
            "customer_id": "CUST-001",
            "policies": [
                {
                    "policy_id": "POL-002",
                    "policy_type": "AUTO",
                    "status": "PENDING",
                }
            ],
        },
    ),
    (
        "EXTRA PROPERTY",
        {
            "customer_id": "CUST-001",
            "policies": [
                {
                    "policy_id": "POL-001",
                    "policy_type": "AUTO",
                    "status": "ACTIVE",
                    "admin": True,
                }
            ],
        },
    ),
]


for name, payload in test_cases:
    print(f"\n=== TEST: {name} ===")

    try:
        result = CustomerPolicies.model_validate(payload)
        print("VALID:", result.model_dump())

    except ValidationError as exc:
        print("REJECTED:")
        for error in exc.errors():
            print(
                "Type:", error["type"],
                "| Field:", error["loc"],
            )