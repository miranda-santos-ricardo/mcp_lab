from datetime import datetime, timezone
from enum import Enum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)

class DomainModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True
    )

class PolicyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"

class Policy(DomainModel):
    policy_id : str = Field(pattern=r"^POL-[0-9]{3}$")
    owner_id : str = Field(min_length=1)
    tenant_id : str = Field(min_length=1)
    status : PolicyStatus
    version : int = Field(ge=1)

class CancellationStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED =  "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    CANCELLED_REQUEST = "CANCELLED_REQUESTED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"

class CancellationRequest(DomainModel):
    request_id : str = Field(pattern=r"^REQ-[0-9]+$")
    policy_id : str = Field(pattern=r"^POL-[0-9]{3}$")

    reason : str = Field(
        min_length=1,
        max_length=1000
    )

    requested_by : str = Field (min_length=1)
    agent_id : str = Field(min_length=1)
    tenant_id : str = Field(min_length=1)

    idempotency_key : str = Field(
        min_length=1,
        max_length=128
    )

    request_fingerprint : str = Field(
        pattern=r"^[a-f0-9]{64}$"
    )

    status : CancellationStatus

    policy_version_at_request : int = Field(ge=1)
    version : int = Field(ge=1)

    created_at : datetime
    updated_at : datetime

    approved_by : str | None = None
    approved_at : datetime | None = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls,value:str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Reason cannot be blank.")

        return value

    @field_validator("created_at","updated_at","approved_at")
    @classmethod
    def require_utc(cls, value: datetime | None):
        
        if value is None:
            return None

        if value.tzinfo is None:
            raise ValueError("Timezone-aware datetime required.")

        if value.utcoffset().total_seconds() != 0 :
            raise ValueError("Datetime must use UTC.")

        return value

    @model_validator(mode="after")
    def validate_invariants(self) -> Self:
        
        if self.updated_at < self.created_at:
            raise ValueError("Updated_at cannot precede created_at")

        if (
            (self.approved_by is None)
            != 
            (self.approved_at is None)
        ):
            raise ValueError("Approval identity and time must coexist")

        if self.status == CancellationStatus.PENDING_APPROVAL :
            if self.approved_by is not None:
                raise ValueError("Pending request cannot have approval ")

        return self

class AuditDecision(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    ERROR = "ERROR"

class AuditEvent(DomainModel):
    event_id : str = Field(min_length=1)
    correlation_id : str = Field(min_length=1)

    timestamp_utc : datetime

    operation : str = Field(min_length=1)
    resource_id : str = Field(min_length=1)

    principal_id : str | None = None
    agent_id : str | None = None
    tenant_id : str | None = None
    request_id : str | None = None

    decision: AuditDecision
    reason_code : str = Field(min_length=1)

    state_before : CancellationStatus | None = None
    state_after : CancellationStatus | None = None

    @field_validator("timestamp_utc")
    @classmethod
    def validate_timestamp(cls, value: datetime):
        if value.tzinfo is None:
            raise ValueError("UTC timezone required.")

        if value.utcoffset().total_seconds() != 0:
            raise ValueError("Timestamp must use UTC.")

        return value

    
