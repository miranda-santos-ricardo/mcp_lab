from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from week2_lab3.week2_lab3_idempotency import (
    IdempotencyScope,
    IdempotencyStore,
    RequestReceipt,
    ReservationStatus,
    calculate_fingerprint,
    OPERATION,
)


def scope(
    principal_id="alice",
    key="K-100",
):
    return IdempotencyScope(
        tenant_id="TENANT-A",
        principal_id=principal_id,
        operation=OPERATION,
        idempotency_key=key,
    )


def fingerprint(reason="Customer requested cancellation"):
    return calculate_fingerprint(
        policy_id="POL-001",
        reason=reason,
    )


def test_01_same_payload_same_fingerprint():
    assert fingerprint() == fingerprint()


def test_02_changed_payload_changes_fingerprint():
    assert fingerprint() != fingerprint(
        "Customer moving abroad"
    )


def test_03_first_call_reserves_operation():
    store = IdempotencyStore()

    result = store.reserve(scope(), fingerprint())

    assert result.status == ReservationStatus.RESERVED
    assert result.reservation_token is not None


def test_04_retry_after_completion():
    store = IdempotencyStore()

    first = store.reserve(scope(), fingerprint())

    store.complete(
        scope(),
        first.reservation_token,
        RequestReceipt(
            request_id="REQ-1001",
            status="PENDING_APPROVAL",
        ),
    )

    retry = store.reserve(scope(), fingerprint())

    assert retry.status == ReservationStatus.REPLAY
    assert retry.receipt.request_id == "REQ-1001"


def test_05_reused_key_with_changed_payload():
    store = IdempotencyStore()

    store.reserve(scope(), fingerprint())

    result = store.reserve(
        scope(),
        fingerprint("Different reason"),
    )

    assert result.status == ReservationStatus.CONFLICT



def test_06_same_key_different_principals():
    store = IdempotencyStore()

    alice = store.reserve(
        scope("alice"),
        fingerprint(),
    )

    bob = store.reserve(
        scope("bob"),
        fingerprint(),
    )

    assert alice.status == ReservationStatus.RESERVED
    assert bob.status == ReservationStatus.RESERVED


def test_07_concurrent_requests_only_one_reserves():
    store = IdempotencyStore()
    barrier = Barrier(2)

    def worker():
        barrier.wait(timeout=5)
        return store.reserve(scope(), fingerprint())

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(lambda _: worker(), range(2))
        )

    statuses = [result.status for result in results]

    assert statuses.count(ReservationStatus.RESERVED) == 1
    assert statuses.count(ReservationStatus.IN_PROGRESS) == 1


def test_08_wrong_token_cannot_complete():
    store = IdempotencyStore()
    store.reserve(scope(), fingerprint())

    with pytest.raises(ValueError):
        store.complete(
            scope(),
            "wrong-token",
            RequestReceipt(
                request_id="REQ-1001",
                status="PENDING_APPROVAL",
            ),
        )


def test_09_abort_allows_retry_when_no_effect():
    store = IdempotencyStore()

    first = store.reserve(scope(), fingerprint())

    store.abort(scope(), first.reservation_token)

    second = store.reserve(scope(), fingerprint())

    assert second.status == ReservationStatus.RESERVED
    assert second.reservation_token != first.reservation_token


def test_10_completed_record_cannot_be_aborted():
    store = IdempotencyStore()

    first = store.reserve(scope(), fingerprint())

    store.complete(
        scope(),
        first.reservation_token,
        RequestReceipt(
            request_id="REQ-1001",
            status="PENDING_APPROVAL",
        ),
    )

    with pytest.raises(ValueError):
        store.abort(scope(), first.reservation_token)