from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt

from shared.infrastructure.config import settings
from ..domain.entities import User
from ..domain.value_objects import Email, HashedPassword, UserRole


class AuthenticationService:
    """
    Serviço de autenticação.

    Maturidade Wardley: COMMODITY
    Em produção delegar inteiramente para Identity Provider externo.
    Anti-Corruption Layer: adaptar tokens externos para o User do domínio.
    """

    def hash_password(self, plain_password: str) -> HashedPassword:
        hashed = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())
        return HashedPassword(hashed.decode())

    def verify_password(self, plain_password: str, hashed: HashedPassword) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed.value.encode())

    def create_access_token(self, user: User) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {
            "sub": user.id,
            "email": user.email.value,
            "role": user.role.value,
            "exp": expire,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
        except Exception:
            return None

    def create_user(self, email: str, password: str, role: str) -> User:
        return User(
            email=Email(email),
            hashed_password=self.hash_password(password),
            role=UserRole(role),
        )