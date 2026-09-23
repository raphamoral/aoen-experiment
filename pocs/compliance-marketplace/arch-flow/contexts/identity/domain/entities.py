from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from shared.kernel.aggregate import AggregateRoot
from .value_objects import Email, HashedPassword, UserRole


@dataclass
class User(AggregateRoot):
    """
    User — Aggregate Root do contexto de Identidade.

    Maturidade Wardley: COMMODITY
    Integrar com OAuth2/OIDC provider em produção (Auth0, Keycloak).
    A lógica de autenticação aqui é mínima e deliberadamente simples.
    """
    email: Email = field(default_factory=lambda: Email("placeholder@example.com"))
    hashed_password: HashedPassword = field(default_factory=lambda: HashedPassword(""))
    role: UserRole = field(default_factory=lambda: UserRole(UserRole.CLIENT))
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    def deactivate(self) -> None:
        self.is_active = False

    def record_login(self) -> None:
        self.last_login = datetime.utcnow()