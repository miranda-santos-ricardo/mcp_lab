from enum import Enum

from pydantic import BaseModel, field

class CancelationStatus(str, Enum):
    """Enum for cancelation status."""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"

class AuthorizationContext:
    principal_id: str
    agent_id: str
    principal_permissions: set[str]
    agent_permissions: set[str]
    tenant_id: str