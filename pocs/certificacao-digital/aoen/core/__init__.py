"""
NÚCLEO (VALOR) — processo isolado de certificação.

Este pacote não importa nada de fora de core/ exceto stdlib e cryptography.
Toda a lógica diferenciadora (assinatura, verificação, hash) vive aqui.
Pode ser extraído para um microserviço ou processo separado sem alterações.
"""