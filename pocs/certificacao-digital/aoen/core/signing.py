"""
Geração e verificação de assinaturas Ed25519.

Ed25519 foi escolhido por:
- Chaves pequenas (32 bytes) → QR codes viáveis
- Verificação ~10x mais rápida que RSA-2048
- Sem parâmetros de curva configuráveis → sem footguns criptográficos
"""
from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
    load_pem_public_key,
)


def generate_keypair() -> tuple[str, str]:
    """Retorna (private_key_pem, public_key_pem) como strings."""
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return private_pem, public_pem


def sign(payload_bytes: bytes, private_key_pem: str) -> str:
    """Assina payload e retorna assinatura hex."""
    private_key: Ed25519PrivateKey = load_pem_private_key(
        private_key_pem.encode(), password=None
    )
    signature_bytes = private_key.sign(payload_bytes)
    return signature_bytes.hex()


def verify(payload_bytes: bytes, signature_hex: str, public_key_pem: str) -> bool:
    """Retorna True se a assinatura for válida para o payload e chave pública."""
    try:
        public_key: Ed25519PublicKey = load_pem_public_key(public_key_pem.encode())
        public_key.verify(bytes.fromhex(signature_hex), payload_bytes)
        return True
    except Exception:
        return False