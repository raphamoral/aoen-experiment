import hashlib
import hmac
import os

# Secret lida em tempo de execução — jamais hardcode em produção.
_SECRET_KEY = os.getenv("CERT_SECRET_KEY", "dev-only-change-in-production").encode()


def generate_certificate_hash(course_id: str, recipient_email: str, issued_at: str) -> str:
    """Gera HMAC-SHA256 para um certificado. Verificável offline sem acesso ao banco."""
    message = f"{course_id}:{recipient_email}:{issued_at}".encode()
    return hmac.new(_SECRET_KEY, message, hashlib.sha256).hexdigest()


def verify_certificate_hash(
    hash_value: str, course_id: str, recipient_email: str, issued_at: str
) -> bool:
    """Verificação timing-safe: previne timing attacks na comparação de hashes."""
    expected = generate_certificate_hash(course_id, recipient_email, issued_at)
    return hmac.compare_digest(expected, hash_value)