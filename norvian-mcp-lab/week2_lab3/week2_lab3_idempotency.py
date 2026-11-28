import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from threading import RLock
from uuid import uuid4

OPERATION = "policy:cancellation:request"

def calculate_fingerprint(
    policy_id: str,
    reason:str
) -> str:
    """Compute a deterministic request fingerprint"""
    payload = {
        "policy_id": policy_id,
        "reason": reason
    }

    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",",":"),
        ensure_ascii=False
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

@dataclass(frozen=True)
class IdempotencyScope:
    tenant_id: str
    principal_id: str
    operation: str
    idempotency_key: str

@dataclass(frozen=True)
class RequestReceipt:
    request_id: str
    status: str

class ReservationStatus(str,Enum):
    RESERVED = "RESERVED"
    REPLAY = "REPLAY"
    CONFLICT = "CONFLICT"
    IN_PROGRESS = "IN_PROGRESS"

@dataclass (frozen=True)
class  ReservationResult:
    status: ReservationStatus
    reservation_token: str | None = None
    receipt: RequestReceipt | None = None

@dataclass
class _StoredRecord:
    fingerprint: str
    reservation_token: str
    receipt: RequestReceipt | None = None

class IdempotencyStore:
    def __init__(self):
        self._records: dict[
            IdempotencyScope, _StoredRecord
        ] = {}
        self._lock = RLock()

    def reserve(
        self,
        scope: IdempotencyScope,
        fingerprint: str,
    ) -> ReservationResult:

        with self._lock:
            existing = self._records.get(scope)

            if existing is not None:

                if existing.fingerprint != fingerprint:
                    return ReservationResult(
                        status=ReservationStatus.CONFLICT
                    )

                if existing.receipt is not None:
                    return ReservationResult(
                        status=ReservationStatus.REPLAY,
                        receipt=existing.receipt,
                    )

                return ReservationResult(
                    status=ReservationStatus.IN_PROGRESS
                )

            token = uuid4().hex

            self._records[scope] = _StoredRecord(
                fingerprint=fingerprint,
                reservation_token=token,
            )

            return ReservationResult(
                status=ReservationStatus.RESERVED,
                reservation_token=token,
            )

    def complete(
        self,
        scope: IdempotencyScope,
        reservation_token: str,
        receipt: RequestReceipt
    ) -> None:
        """Store the completed operation result."""
        with self._lock:
            record = self._records.get(scope)

            if (
                record is None
                or record.reservation_token != reservation_token
                or record.receipt is not None
            ):
                raise ValueError("INVALID_RESERVATION")

            record.receipt = receipt

    def abort(
        self,
        scope: IdempotencyScope,
        reservation_token: str
    ) -> None:
        """
        Release an unfinished reservation.

        Safe to use only when the caller has established
        that no business side effect was committed.
        """
        with self._lock:
            record = self._records.get(scope)

            if (
                record is None
                or record.reservation_token != reservation_token
                or record.receipt is not None
            ):
                raise ValueError("INVALID_RESERVATION")

            del self._records[scope]