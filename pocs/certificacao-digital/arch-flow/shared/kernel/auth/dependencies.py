import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-inseguro-troque-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

security = HTTPBearer()


def criar_token(dados: dict, expira_em: Optional[timedelta] = None) -> str:
    payload = dados.copy()
    expiracao = datetime.now(timezone.utc) + (
        expira_em or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expiracao})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        return jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def estudante_atual(token: dict = Depends(verificar_token)) -> str:
    estudante_id = token.get("sub")
    if not estudante_id:
        raise HTTPException(status_code=401, detail="Token sem identificação de estudante")
    return estudante_id