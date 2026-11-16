import pytest
from week2_lab222_authorization import (
    build_trusted_context,
    authorize_cancellation_request
)


@pytest.mark.parametrize(
    "principal, agent, policy_id, expected_allowed, expected_reason",
    [
        (
            "alice",
            "insurance-agent",
            "POL-001",
            True,
            "AUTHORIZED",
        ),
        (
            "bob",
            "insurance-agent",
            "POL-001",
            False,
            "RESOURCE_NOT_ACCESSIBLE",
        ),
        (
            "charlie",
            "insurance-agent",
            "POL-001",
            False,
            "USER_PERMISSION_DENIED",
        ),
        (
            "alice",
            "read-only-agent",
            "POL-001",
            False,
            "AGENT_PERMISSION_DENIED",
        ),
        (
            "alice",
            "insurance-agent",
            "POL-003",
            False,
            "RESOURCE_NOT_ACCESSIBLE",
        ),
        (
            "alice",
            "insurance-agent",
            "POL-999",
            False,
            "RESOURCE_NOT_ACCESSIBLE",
        ),
        (
            "bob",
            "insurance-agent",
            "POL-002",
            True,
            "AUTHORIZED",
        ),
    ],
)
def test_authorized_matrix(
    principal,
    agent,
    policy_id,
    expected_allowed,
    expected_reason
):
    context = build_trusted_context(principal, agent)
    decision = authorize_cancellation_request(context=context, policy_id=policy_id)

    assert decision.allowed is expected_allowed
    assert decision.reason_code == expected_reason

def test_unknow_identity_denied():
    with pytest.raises(PermissionError):
        build_trusted_context("unknown-user","insurance-agent")

def test_undelegated_agent_denied():
    with pytest.raises(PermissionError):
        build_trusted_context("Bob","read-only-agent")