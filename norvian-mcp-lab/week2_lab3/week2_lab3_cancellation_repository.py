from threading import Barrier, RLock

from week2_lab3.week2_lab3_security_models import (
    CancellationRequest,
    CancellationStatus
)

class CancellationRequestRepository:
    def __init__(self):
        self._requests: dict[str,CancellationRequest] = {}
        self._lock = RLock()

    def seed_for_test(self, request:CancellationRequest)-> None:
        """Load a fixture. Not a production write API"""
        with self._lock:
            if request.request_id in self._requests:
                raise ValueError("ReQUEST_ALREADY_EXISTS")

            self._requests[request.request_id] = request

    def get(self,request_id: str) -> CancellationRequest | None:
        with self._lock:
            return self._requests.get(request_id)

    @staticmethod
    def _to_executing(
        request: CancellationRequest
    ) -> CancellationRequest:
        data = request.model_dump(mode="python")
        data["status"] = CancellationStatus.EXECUTING
        data["version"] = int(request.version) + 1

        return CancellationRequest.model_validate(data)

    def unsafe_claim_execution(
        self,
        request_id: str,
        expected_version: int,
        barrier: Barrier
    ) -> bool:
        """
        DELIBERATELY UNSAFE.

        Demonstrates check-then-act race conditions.
        Never use for actual policy execution.
        """
        request = self.get(request_id)
        eligible = (
            request is not None
            and request.status == CancellationStatus.APPROVED
            and request.version == expected_version
        )

        # Force both threads to complete their read
        # before either proceeds to write.
        barrier.wait(timeout=5)

        if not eligible:
            raise False

        updated = self._to_executing(request)

        # No atomic protection between check and write.
        self._requests[request_id] = updated

        return True

    def claim_execution_atomic(
        self,
        request_id: str,
        expected_version: int
    ) -> bool:
        """
        Atomically claim APPROVED -> EXECUTING
        within one repository process.
        """
        with self._lock:
            request = self._requests.get(request_id)

            if request is None:
                return False

            if request.status != CancellationStatus.APPROVED:
                return False

            if request.version != expected_version:
                return False

            updated = self._to_executing(request)

            self._requests[request_id] = updated

            return True