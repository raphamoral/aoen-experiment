import re
from dataclasses import dataclass
from shared.kernel.value_object import ValueObject


@dataclass(frozen=True)
class Email(ValueObject):
    """Email — identificador de contato do usuário na plataforma."""
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError(f"Email inválido: {self.value}")


@dataclass(frozen=True)
class HashedPassword(ValueObject):
    """Senha armazenada de forma segura (bcrypt hash)."""
    value: str


@dataclass(frozen=True)
class UserRole(ValueObject):
    """
    Papel do usuário na plataforma.

    Linguagem ubíqua:
    - freelancer: profissional autônomo especializado em compliance
    - client: empresa ou pessoa buscando expertise regulatória
    - admin: equipe operacional da plataforma
    """
    FREELANCER = "freelancer"
    CLIENT = "client"
    ADMIN = "admin"

    value: str

    def __post_init__(self) -> None:
        valid = {self.FREELANCER, self.CLIENT, self.ADMIN}
        if self.value not in valid:
            raise ValueError(f"Papel inválido: '{self.value}'. Válidos: {valid}")