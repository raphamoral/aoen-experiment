import hashlib
import json

from ports.outbound.hashing_service_port import HashingServicePort


class SHA256HashingService(HashingServicePort):
    """
    Driven adapter: produces a deterministic SHA-256 hash from the core
    certificate fields.

    The canonical JSON serialisation (sorted keys, ASCII-safe) ensures
    the same hash is always produced for the same inputs regardless of
    the platform or Python version.  This hash is the public verification
    token: sharing it is sufficient to prove authenticity.
    """

    def hash_certificate_data(
        self,
        certificate_id: str,
        student_id: str,
        course_id: str,
        issued_at: str,
        issuer_name: str,
    ) -> str:
        payload = {
            "certificate_id": certificate_id,
            "course_id": course_id,
            "issued_at": issued_at,
            "issuer_name": issuer_name,
            "student_id": student_id,
        }
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()