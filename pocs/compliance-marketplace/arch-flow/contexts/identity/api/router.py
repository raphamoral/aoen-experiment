from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from ..application.services import AuthenticationService
from ..domain.entities import User
from ..domain.value_objects import UserRole

router = APIRouter(prefix="/identity", tags=["Identity (Commodity)"])
auth_service = AuthenticationService()

# Repositório em memória — substituir por DB + OAuth provider em produção
_users: dict[str, User] = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/identity/token")


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = UserRole.CLIENT


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Registra novo usuário na plataforma."""
    existing = any(u.email.value == request.email for u in _users.values())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado"
        )
    user = auth_service.create_user(request.email, request.password, request.role)
    _users[user.id] = user
    return {"user_id": user.id, "email": user.email.value, "role": user.role.value}


@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Autentica usuário e retorna JWT."""
    user = next(
        (u for u in _users.values() if u.email.value == form_data.username), None
    )
    if not user or not auth_service.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
    user.record_login()
    token = auth_service.create_access_token(user)
    return TokenResponse(access_token=token)