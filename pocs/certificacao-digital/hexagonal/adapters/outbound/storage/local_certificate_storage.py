import logging
from pathlib import Path

from ports.outbound.certificate_storage_port import CertificateStoragePort

logger = logging.getLogger(__name__)


class LocalCertificateStorage(CertificateStoragePort):
    """
    Driven adapter: persists certificate artifacts as plain-text files on the
    local filesystem.

    Replace with an S3Adapter, GCSAdapter, or IPFSAdapter without touching
    a single line of domain or application code — that is the hexagonal
    guarantee.
    """

    def __init__(self, storage_dir: str = "./certificates_storage") -> None:
        self._root = Path(storage_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    def store_certificate(
        self,
        certificate_id: str,
        student_name: str,
        course_name: str,
        issuer_name: str,
        duration_hours: int,
        issued_at: str,
        certificate_hash: str,
    ) -> str:
        path = self._root / f"{certificate_id}.txt"
        content = (
            "╔══════════════════════════════════════════════════╗\n"
            "║         CERTIFICADO DIGITAL — CURSO LIVRE        ║\n"
            "╚══════════════════════════════════════════════════╝\n\n"
            f"  Estudante   : {student_name}\n"
            f"  Curso       : {course_name}\n"
            f"  Emissor     : {issuer_name}\n"
            f"  Carga horária: {duration_hours} h\n"
            f"  Emitido em  : {issued_at}\n\n"
            f"  ID          : {certificate_id}\n"
            f"  Hash SHA-256: {certificate_hash}\n\n"
            "  Este documento pode ser verificado publicamente\n"
            "  pelo hash acima na plataforma de certificação.\n"
        )
        path.write_text(content, encoding="utf-8")
        logger.info("Certificate artifact stored at %s", path)
        return str(path)

    def delete_certificate(self, certificate_id: str) -> None:
        path = self._root / f"{certificate_id}.txt"
        if path.exists():
            path.unlink()
            logger.info("Certificate artifact deleted: %s", path)