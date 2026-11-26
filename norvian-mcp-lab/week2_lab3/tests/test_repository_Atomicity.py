from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier

from week2_lab3.week2_lab3_security_models import (
    CancellationStatus,
    CancellationRequest
)

from week2_lab3.week2_lab3_cancellation_repository import (
    CancellationRequestRepository
)

NOW = datetime(2026,11,23,tzinfo=timezone.utc)

def approved_request():
    """Internal fixture; does not prove human approval."""
    return CancellationRequest(
        request_id='REQ-1001',
        policy_id='POL-001',
        reason="Customer requested cancellation",
        requested_by="alice",
        agent_id="insurance-agent",
        tenant_id="TENANT-A",
        idempotency_key="K-100",
        request_fingerprint="a"*64,
        status=CancellationStatus.APPROVED,
        policy_version_at_request=1,
        version=3,
        created_at=NOW,
        updated_at=NOW,
        approved_by="maria",
        approved_at=NOW
    )

def test_01_unsafe_race_condition():
    repository = CancellationRequestRepository()
    repository.seed_for_test(approved_request())

    barrier = Barrier(2)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                repository.unsafe_claim_execution,
                "REQ-1001",
                3,
                barrier,
            )
            for _ in range(2)
        ]

        results = [f.result() for f in futures]

    # Both workers incorrectly believe they acquired
    # the same execution right.
    assert results.count(True) == 2


def test_02_atomic_claim_allows_only_one_worker():
    repository = CancellationRequestRepository()
    repository.seed_for_test(approved_request())

    barrier = Barrier(2)

    def worker():
        barrier.wait(timeout=5)

        return repository.claim_execution_atomic(
            request_id="REQ-1001",
            expected_version=3,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: worker(), range(2)))

    assert results.count(True) == 1
    assert results.count(False) == 1

    request = repository.get("REQ-1001")

    assert request.status == CancellationStatus.EXECUTING
    assert request.version == 4



def test_03_stale_version_is_rejected():
    repository = CancellationRequestRepository()
    repository.seed_for_test(approved_request())

    result = repository.claim_execution_atomic(
        request_id="REQ-1001",
        expected_version=2,
    )

    assert result is False

    request = repository.get("REQ-1001")
    assert request.version == 3
    assert request.status == CancellationStatus.APPROVED


def test_04_repeated_claim_is_rejected():
    repository = CancellationRequestRepository()
    repository.seed_for_test(approved_request())

    first = repository.claim_execution_atomic(
        request_id="REQ-1001",
        expected_version=3,
    )

    second = repository.claim_execution_atomic(
        request_id="REQ-1001",
        expected_version=3,
    )

    assert first is True
    assert second is False

    request = repository.get("REQ-1001")
    assert request.version == 4


def test_05_unknown_request_is_rejected():
    repository = CancellationRequestRepository()

    result = repository.claim_execution_atomic(
        request_id="REQ-9999",
        expected_version=1,
    )

    assert result is False