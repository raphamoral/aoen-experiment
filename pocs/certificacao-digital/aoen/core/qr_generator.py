"""
Geração de QR Code para URL de verificação pública.

MULTI-INTERFACE: o QR code é a interface física — permite verificação
offline (visualmente) e online (scan → URL) a partir do mesmo certificado impresso.
"""
from __future__ import annotations

import base64
import io

import qrcode
from qrcode.image.pure import PyPNGImage


def build_verification_url(base_url: str, public_id: str) -> str:
    return f"{base_url.rstrip('/')}/verify/{public_id}"


def generate_qr_base64(url: str) -> str:
    """Retorna PNG do QR code encodado em base64 (embed em HTML/PDF)."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=PyPNGImage)
    buffer = io.BytesIO()
    img.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode()