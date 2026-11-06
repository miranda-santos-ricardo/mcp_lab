from typing import Literal

from pydantic import BaseModel, ConfigDict, Field 

class ContractModel(BaseModel):

    model_config = ConfigDict(extra="forbid")

class CustomerProfile(ContractModel):
    customer_id: str = Field(
        pattern=r"^CUST-[0-9]{3}$"
    )
    full_name: str = Field(min_length=1)
    status: Literal["ACTIVE","INACTIVE"]

class Policy(ContractModel):
    policy_id: str = Field(
        pattern=r"^POL-[0-9]{3}$"
    )
    policy_type: Literal["LIFE","HOME","AUTO"]
    status: Literal["ACTIVE","INACTIVE", "CANCELED"]

class CustomerPolicies(ContractModel):
    customer_id: str 
    policies: list[Policy] = Field(min_length=0)