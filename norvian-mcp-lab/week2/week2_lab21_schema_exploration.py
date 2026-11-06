import json

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError
)

class GetCustomerProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    customer_id: str = Field(
        pattern="^CUST-[0-9]{3}$",
        description="Customer ID in the CUST-NNN format",
    )

print("\n ==== 1. GENERATED JSON SCHEMA")
schema = GetCustomerProfileInput.model_json_schema()

print(json.dumps(schema, indent=2))

test_cases = [
    ("VALID", {"customer_id": "CUST-001"}),
    ("INVALI_FORMAT", {"customer_id":"ABC-123"}),
    ("MISSING FIELD", {}),
    ("EXTRA FIELD",{
        "customer_id": "CUST-001",
        "admin": True,
    }),
    ("NULL VALUE", {"customer_id": None})
]

for name, payload in test_cases:
    print(f"\n===2. TEST {name} =======")

    try:
        result = GetCustomerProfileInput.model_validate(payload)
        print("VALID",result.model_dump())

    except ValidationError as exc:
        print("REJECTED:")
        for error in exc.errors():
            print(
                "Type:",error["type"],
                "| field:", error["loc"]
            )