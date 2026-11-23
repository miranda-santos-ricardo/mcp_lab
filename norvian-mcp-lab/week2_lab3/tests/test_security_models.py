from datetime import datetime, timezone, timedelta

import pytest
from pydantic import ValidationError

from week2_lab3.week2_lab3_security_models import (
    Policy,
    PolicyStatus,
    CancellationStatus,
    CancellationRequest,
    AuditEvent,
    AuditDecision
)

NOW = datetime(2026,11,22,tzinfo=timezone.utc)

def valid_request_data():
    return {
        "request_id": "REQ-1001",
        "policy_id": "POL-001",
        "reason": "Customer requested cancellation",
        "requested_by": "alice",
        "agent_id": "insurance-agent",
        "tenant_id": "TENANT-A",
        "idempotency_key": "K-100",
        "request_fingerprint": "a" * 64,
        "status": CancellationStatus.PENDING_APPROVAL,
        "policy_version_at_request": 1,
        "version": 1,
        "created_at": NOW,
        "updated_at": NOW,
    }

def test_01_valid_policy():
    policy = Policy(
        policy_id = "POL-001",
        owner_id = "alice",
        tenant_id= "TENANT-A",
        status = PolicyStatus.ACTIVE,
        version = 1
    )

    assert policy.status == PolicyStatus.ACTIVE

def test_02_extra_fields_are_rejected():
    data = valid_request_data()
    data["admin"] = True

    with pytest.raises(ValidationError):
        CancellationRequest(**data)

def test_03_pending_request_cannot_have_approval():
    data = valid_request_data()
    data["approved_by"] = "maria"
    data["approved_at"] = NOW

    with pytest.raises(ValidationError):
        CancellationRequest(**data)

def test_04_invalid_timestamp_order():
    data =  valid_request_data()
    data["updated_at"] = NOW - timedelta(minutes=1)

    with pytest.raises(ValidationError):
        CancellationRequest(**data)




def test_05_blank_reason_rejected():
    data = valid_request_data()
    data["reason"] = " "

    with pytest.raises(ValueError):
        CancellationRequest(**data)


def test_06_request_is_immutable():
    request = CancellationRequest(**valid_request_data())

    with pytest.raises(ValidationError):
        request.status = CancellationStatus.EXECUTED


def test_07_naive_datetime_rejected():
    data = valid_request_data()
    data["created_at"] = datetime(2026, 11, 22, 10, 0)

    with pytest.raises(ValidationError):
        CancellationRequest(**data)


def test_08_valid_audit_event():
    event = AuditEvent(
        event_id="EVT-001",
        correlation_id="CORR-001",
        timestamp_utc=NOW,
        operation="policy:cancellation:request",
        resource_id="POL-001",
        principal_id="alice",
        agent_id="insurance-agent",
        tenant_id="TENANT-A",
        request_id="REQ-1001",
        decision=AuditDecision.ALLOWED,
        reason_code="REQUEST_CREATED",
        state_after=CancellationStatus.PENDING_APPROVAL,
    )

    assert event.decision == AuditDecision.ALLOWED

