import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    valor: str

    def __post_init__(self):
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", self.valor):
            raise ValueError(f"Email inválido: {self.valor}")

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class NomeCompleto:
    valor: str

    def __post_init__(self):
        if len(self.valor.strip()) < 3:
            raise ValueError("Nome completo deve ter ao menos 3 caracteres.")

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class HashDeVerificacao:
    """
    Identificador público único de um certificado.
    Permite verificação sem expor IDs internos ou dados sensíveis.
    Wardley: Custom — evoluirá para W3C Verifiable Credentials (Genesis→Product).
    """
    valor: str

    def __str__(self) -> str:
        return self.valor

    @property
    def url_publica(self) -> str:
        return f"/api/v1/verificacao/{self.valor}"