from datetime import date
from typing import Literal

from  pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
)

class PolicyV1Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: str
    policy_type: Literal["AUTO", "HOME", "LIFE"]
    status: Literal["ACTIVE", "CANCELLED"]

class PolicyV1Permissive(BaseModel):
    model_config = ConfigDict(extra="ignore")

    policy_id: str
    policy_type: Literal["AUTO", "HOME", "LIFE"]
    status: Literal["ACTIVE", "CANCELLED"]

class PolicyV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: str
    policy_type: Literal["AUTO", "HOME", "LIFE"]
    status: Literal["ACTIVE", "CANCELLED"]
    renewal_date: date | None = None

old_payload = {
    "policy_id":"POL-001",
    "policy_type":"AUTO",
    "status":"ACTIVE"
}

new_payload = {
    "policy_id":"POL-001",
    "policy_type":"AUTO",
    "status":"ACTIVE",
    "renewal_date":"2027-05-15"
}

def evaluate(name: str, model: type[BaseModel], payload: dict):
    print(f"\n=== {name} ===")

    try:
        result = model.model_validate(payload)
        print("ACCEPTED:", result.model_dump(mode="json"))

    except ValidationError as exc:
        print("REJECTED:")
        for error in exc.errors():
            print(
                "Type:", error["type"],
                "| Field:", error["loc"],
            )


evaluate(
    "1. V1 Strict receives V1 payload",
    PolicyV1Strict,
    old_payload,
)

evaluate(
    "2. V1 Strict receives V2 payload",
    PolicyV1Strict,
    new_payload,
)

evaluate(
    "3. V1 Permissive receives V2 payload",
    PolicyV1Permissive,
    new_payload,
)

evaluate(
    "4. V2 receives V1 payload",
    PolicyV2,
    old_payload,
)

evaluate(
    "5. V2 receives V2 payload",
    PolicyV2,
    new_payload,
)